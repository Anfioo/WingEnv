#[macro_export]
macro_rules! all_commands {
    ($app:expr) => {
        $app.invoke_handler(tauri::generate_handler![
            // 在这里把你所有文件的命令列出来
            crate::commands::app::greet,
            crate::commands::tray::update_tray_menu,
            crate::commands::setup::set_complete
        ])
    };
}

