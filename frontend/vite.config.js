import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Vite options tailored for Tauri development and only applied in `tauri dev` or `tauri build`
  // prevent vite from obscuring rust errors
  clearScreen: false,
  // tauri expects a fixed port, fail if that port is not available
  server: {
    port: 5173,
    strictPort: true,
    watch: {
      // watch all but node_modules
      ignored: ["**/node_modules/**"],
    },
  },
  // to make use of `TAURI_DEBUG` and other env variables
  // https://tauri.app/v1/api/config#build
  envPrefix: ["VITE_", "TAURI_"],
});
