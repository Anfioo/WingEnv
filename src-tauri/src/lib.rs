mod plugins;

use std::sync::Mutex;
use tauri::async_runtime::spawn;
use tauri::{AppHandle, Manager, State};
use tokio::time::{sleep, Duration};

// Setup state to track frontend and backend task completion
struct SetupState {
    frontend_task: bool,
    backend_task: bool,
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn update_tray_menu(
    app: tauri::AppHandle,
    show_text: String,
    quit_text: String,
) -> Result<(), String> {
    plugins::system_tray::update_tray_menu(&app, &show_text, &quit_text)
}

#[tauri::command]
async fn set_complete(
    app: AppHandle,
    state: State<'_, Mutex<SetupState>>,
    task: String,
) -> Result<(), ()> {
    let mut state_lock = state.lock().unwrap();
    match task.as_str() {
        "frontend" => state_lock.frontend_task = true,
        "backend" => state_lock.backend_task = true,
        _ => panic!("invalid task completed!"),
    }

    if state_lock.backend_task && state_lock.frontend_task {
        let splash_window = app.get_webview_window("splashscreen").unwrap();
        let main_window = app.get_webview_window("main").unwrap();
        splash_window.close().unwrap();
        main_window.show().unwrap();
    }
    Ok(())
}

async fn setup(app: AppHandle) -> Result<(), ()> {
    println!("Performing really heavy backend setup task...");
    let arch = tauri_plugin_os::arch();
    let exe_extension = tauri_plugin_os::exe_extension();
    let family = tauri_plugin_os::family();
    let locale = tauri_plugin_os::locale();
    let platform = tauri_plugin_os::platform();
    let version = tauri_plugin_os::version();

    println!("=== OS Information ===");
    println!("Arch: {}", arch);
    println!("Exe Extension: {}", exe_extension);
    println!("Family: {}", family);
    println!("Locale: {:?}", locale);
    println!("Platform: {}", platform);
    println!("Version: {}", version);
    println!("=======================");
    println!("Platform: {}", platform);
    // 将 "windows" 输出到终端

    sleep(Duration::from_secs(3)).await;
    println!("Backend setup task completed!");

    set_complete(
        app.clone(),
        app.state::<Mutex<SetupState>>(),
        "backend".to_string(),
    )
    .await?;
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let builder = tauri::Builder::default()
        .plugin(tauri_plugin_window_state::Builder::new().build())
        .plugin(tauri_plugin_os::init())
        .manage(Mutex::new(SetupState {
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
        .invoke_handler(tauri::generate_handler![
            greet,
            update_tray_menu,
            set_complete
        ])
        .setup(|app| {
            spawn(setup(app.handle().clone()));
            Ok(())
        });

    // Only enable updater in release mode
    #[cfg(not(debug_assertions))]
    let builder = builder.plugin(tauri_plugin_updater::Builder::new().build());

    builder
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
