use std::sync::Mutex;
use tauri::{AppHandle, Manager, State};
use tokio::time::{sleep, Duration};

// Setup state to track frontend and backend task completion
pub struct SetupState {
     pub(crate) frontend_task: bool,
     pub(crate) backend_task: bool,
}

#[tauri::command]
pub async fn set_complete(
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

pub async fn setup(app: AppHandle) -> Result<(), ()> {
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
