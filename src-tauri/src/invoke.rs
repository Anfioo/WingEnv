#[macro_export]
macro_rules! all_commands {
    ($app:expr) => {
        $app.invoke_handler(tauri::generate_handler![
            crate::commands::greet::greet,
            crate::commands::tray::update_tray_menu
        ])
    };
}
