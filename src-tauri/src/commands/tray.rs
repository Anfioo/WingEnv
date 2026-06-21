
#[tauri::command]
pub fn update_tray_menu(
    app: tauri::AppHandle,
    show_text: String,
    quit_text: String,
) -> Result<(), String> {
    crate::plugins::system_tray::update_tray_menu(&app, &show_text, &quit_text)
}
