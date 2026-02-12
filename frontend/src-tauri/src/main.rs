use tauri::Manager;

fn main() {
  tauri::Builder::default()
    .setup(|app| {
      let _app_handle = app.handle();
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
