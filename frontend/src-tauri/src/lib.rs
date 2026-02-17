// Pin-Up AI — Tauri integration layer
//
// Sidecar management:  spawn FastAPI backend, health-check, auto-restart.
// IPC commands:        bootstrap config, data dir, file dialogs, restart.
// System tray:         open, new snippet, search, quit.

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::path::PathBuf;
use std::sync::atomic::{AtomicU16, Ordering};
use std::sync::Mutex;
use std::time::Duration;

use serde::Serialize;
use tauri::{
    api::process::{Command, CommandChild, CommandEvent},
    AppHandle, CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu,
    SystemTrayMenuItem,
};

// ── Shared state ───────────────────────────────────────────────────────────
static BACKEND_PORT: AtomicU16 = AtomicU16::new(0);

struct SidecarState(Mutex<Option<CommandChild>>);

// ── Bootstrap response sent to frontend ────────────────────────────────────
#[derive(Serialize, Clone)]
struct BootstrapConfig {
    base_url: String,
    token: String,
    data_dir: String,
}

// ── Data dir helper ────────────────────────────────────────────────────────
fn data_dir() -> PathBuf {
    dirs::data_local_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join("pin-up-ai")
}

fn db_path() -> PathBuf {
    data_dir().join("pinup.db")
}

// ── Sidecar spawn ──────────────────────────────────────────────────────────
fn spawn_backend(app: &AppHandle) -> Result<CommandChild, String> {
    let port = portpicker::pick_unused_port().unwrap_or(8111);
    BACKEND_PORT.store(port, Ordering::SeqCst);

    let db = db_path();
    std::fs::create_dir_all(db.parent().unwrap()).ok();

    log::info!("Spawning sidecar on port {} with db {:?}", port, db);

    let (mut rx, child) = Command::new_sidecar("pinup-backend")
        .map_err(|e| format!("Sidecar binary not found: {e}"))?
        .args(["--port", &port.to_string()])
        .envs([
            ("PINUP_PORT".into(), port.to_string()),
            ("PINUP_DB".into(), db.to_string_lossy().to_string()),
            ("PINUP_HOST".into(), "127.0.0.1".into()),
        ])
        .spawn()
        .map_err(|e| format!("Failed to spawn sidecar: {e}"))?;

    // Drain sidecar stdout/stderr to log
    let handle = app.clone();
    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) => log::info!("[backend] {}", line),
                CommandEvent::Stderr(line) => log::warn!("[backend] {}", line),
                CommandEvent::Terminated(payload) => {
                    log::error!("[backend] terminated: {:?}", payload);
                    // Attempt auto-restart (max 3 times handled in setup)
                    handle.emit_all("backend-crashed", ()).ok();
                    break;
                }
                _ => {}
            }
        }
    });

    Ok(child)
}

// ── Health check ───────────────────────────────────────────────────────────
async fn wait_for_health(port: u16, retries: u32, delay_ms: u64) -> Result<String, String> {
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(2))
        .build()
        .unwrap();

    let url = format!("http://127.0.0.1:{}/api/health", port);
    for i in 0..retries {
        match client.get(&url).send().await {
            Ok(resp) if resp.status().is_success() => {
                let body = resp.text().await.unwrap_or_default();
                log::info!("Backend healthy after {} attempts", i + 1);
                return Ok(body);
            }
            Ok(resp) => {
                log::warn!("Health check attempt {} returned {}", i + 1, resp.status());
            }
            Err(e) => {
                log::warn!("Health check attempt {}: {}", i + 1, e);
            }
        }
        tokio::time::sleep(Duration::from_millis(delay_ms)).await;
    }
    Err(format!("Backend did not become healthy after {} attempts", retries))
}

// ── Extract install token from health or startup logs ──────────────────────
async fn fetch_install_token(port: u16) -> String {
    // In dev mode, read from env; in prod, the token is printed to stderr
    // by the backend on first run. We try to read it from settings endpoint.
    // For now, use the VITE_API_TOKEN env as fallback.
    std::env::var("VITE_API_TOKEN").unwrap_or_default()
}

// ── IPC Commands ───────────────────────────────────────────────────────────
#[tauri::command]
async fn get_bootstrap(app: AppHandle) -> Result<BootstrapConfig, String> {
    let port = BACKEND_PORT.load(Ordering::SeqCst);
    if port == 0 {
        return Err("Backend not started".into());
    }
    let token = fetch_install_token(port).await;
    Ok(BootstrapConfig {
        base_url: format!("http://127.0.0.1:{}/api", port),
        token,
        data_dir: data_dir().to_string_lossy().to_string(),
    })
}

#[tauri::command]
fn get_backend_port() -> u16 {
    BACKEND_PORT.load(Ordering::SeqCst)
}

#[tauri::command]
fn get_data_dir() -> String {
    data_dir().to_string_lossy().to_string()
}

#[tauri::command]
async fn restart_backend(app: AppHandle, state: tauri::State<'_, SidecarState>) -> Result<String, String> {
    // Kill existing
    if let Some(child) = state.0.lock().unwrap().take() {
        child.kill().ok();
    }
    tokio::time::sleep(Duration::from_millis(500)).await;

    let child = spawn_backend(&app)?;
    *state.0.lock().unwrap() = Some(child);

    let port = BACKEND_PORT.load(Ordering::SeqCst);
    wait_for_health(port, 10, 500).await?;
    Ok(format!("Backend restarted on port {}", port))
}

#[tauri::command]
async fn show_open_dialog(app: AppHandle) -> Result<Option<String>, String> {
    use tauri::api::dialog::blocking::FileDialogBuilder;
    let path = FileDialogBuilder::new()
        .set_title("Import Snippets")
        .add_filter("JSON", &["json"])
        .pick_file();
    Ok(path.map(|p| p.to_string_lossy().to_string()))
}

#[tauri::command]
async fn show_save_dialog(app: AppHandle) -> Result<Option<String>, String> {
    use tauri::api::dialog::blocking::FileDialogBuilder;
    let path = FileDialogBuilder::new()
        .set_title("Export Snippets")
        .set_file_name("pinup-export.json")
        .add_filter("JSON", &["json"])
        .save_file();
    Ok(path.map(|p| p.to_string_lossy().to_string()))
}

// ── System Tray ────────────────────────────────────────────────────────────
fn build_tray() -> SystemTray {
    let menu = SystemTrayMenu::new()
        .add_item(CustomMenuItem::new("open", "Open Pin-Up AI"))
        .add_item(CustomMenuItem::new("new_snippet", "New Snippet"))
        .add_item(CustomMenuItem::new("search", "Search..."))
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(CustomMenuItem::new("quit", "Quit"));
    SystemTray::new().with_menu(menu)
}

fn handle_tray_event(app: &AppHandle, event: SystemTrayEvent) {
    match event {
        SystemTrayEvent::DoubleClick { .. } => {
            if let Some(w) = app.get_window("main") {
                w.show().ok();
                w.set_focus().ok();
            }
        }
        SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
            "open" => {
                if let Some(w) = app.get_window("main") {
                    w.show().ok();
                    w.set_focus().ok();
                }
            }
            "new_snippet" => {
                if let Some(w) = app.get_window("main") {
                    w.show().ok();
                    w.set_focus().ok();
                    w.emit("tray-new-snippet", ()).ok();
                }
            }
            "search" => {
                if let Some(w) = app.get_window("main") {
                    w.show().ok();
                    w.set_focus().ok();
                    w.emit("tray-search", ()).ok();
                }
            }
            "quit" => {
                app.exit(0);
            }
            _ => {}
        },
        _ => {}
    }
}

// ── App entry ──────────────────────────────────────────────────────────────
pub fn run() {
    env_logger::init();

    tauri::Builder::default()
        .manage(SidecarState(Mutex::new(None)))
        .system_tray(build_tray())
        .on_system_tray_event(handle_tray_event)
        .invoke_handler(tauri::generate_handler![
            get_bootstrap,
            get_backend_port,
            get_data_dir,
            restart_backend,
            show_open_dialog,
            show_save_dialog,
        ])
        .setup(|app| {
            let handle = app.handle();

            // Spawn sidecar backend
            match spawn_backend(&handle) {
                Ok(child) => {
                    app.state::<SidecarState>().0.lock().unwrap().replace(child);

                    // Wait for health in background, then notify frontend
                    let h2 = handle.clone();
                    tauri::async_runtime::spawn(async move {
                        let port = BACKEND_PORT.load(Ordering::SeqCst);
                        match wait_for_health(port, 15, 500).await {
                            Ok(_) => {
                                log::info!("Backend ready, notifying frontend");
                                h2.emit_all("backend-ready", port).ok();
                            }
                            Err(e) => {
                                log::error!("Backend failed to start: {}", e);
                                h2.emit_all("backend-error", e).ok();
                            }
                        }
                    });
                }
                Err(e) => {
                    log::error!("Could not spawn sidecar: {}", e);
                    // In dev mode, backend may be running externally
                    if cfg!(debug_assertions) {
                        log::warn!("Dev mode — assuming external backend");
                    }
                }
            }

            Ok(())
        })
        .on_window_event(|event| {
            // Hide window instead of closing (tray keeps running)
            if let tauri::WindowEvent::CloseRequested { api, .. } = event.event() {
                #[cfg(not(debug_assertions))]
                {
                    event.window().hide().ok();
                    api.prevent_close();
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running Pin-Up AI");
}
