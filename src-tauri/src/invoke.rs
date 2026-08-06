#[macro_export]
macro_rules! all_commands {
    ($app:expr) => {
        $app.invoke_handler(tauri::generate_handler![
            crate::commands::greet::greet,
            crate::commands::progress::run_progress_demo,
            crate::commands::tray::update_tray_menu,
            crate::commands::updater::cancel_update_download,
            crate::commands::updater::download_and_install_update,
            crate::commands::updater::is_update_download_active
        ])
    };
}
