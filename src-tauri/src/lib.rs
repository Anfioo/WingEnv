mod commands;
mod invoke;
mod plugins;

use std::sync::Mutex;
use tauri::async_runtime::spawn;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let builder = tauri::Builder::default()
        .plugin(tauri_plugin_window_state::Builder::new().build())
        .plugin(tauri_plugin_os::init())
        .manage(Mutex::new(commands::setup::SetupState {
            frontend_task: false,
            backend_task: false,
        }))
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.set_focus();
                let _ = window.unminimize();
                let _ = window.show();
            }
        }))
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .plugin(plugins::system_tray::init())
        .setup(|app| {
            spawn(commands::setup::setup(app.handle().clone()));
            Ok(())
        });

    // Only enable updater in release mode
    #[cfg(not(debug_assertions))]
    let builder = builder.plugin(tauri_plugin_updater::Builder::new().build());
    // 注册所有的命令
    let _builder = all_commands!(builder);
    _builder
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
