

#[tauri::command]
/// 这是一个问候函数
///
/// # 参数
/// * `name` - 要问候的人的名字
///
/// # 返回值
/// 返回一个拼接好的问候字符串
pub fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}
