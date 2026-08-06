use std::thread;
use std::time::Duration;

use serde::Serialize;
use tauri::ipc::Channel;

#[derive(Clone, Serialize)]
pub struct ProgressPayload {
    pub current: u32,
    pub total: u32,
    pub message: String,
}

#[tauri::command]
pub fn run_progress_demo(on_progress: Channel<ProgressPayload>) -> Result<(), String> {
    thread::spawn(move || {
        for current in 0..=100 {
            let message = match current {
                0..=25 => "Starting".to_string(),
                26..=50 => "Working".to_string(),
                51..=75 => "Almost there".to_string(),
                _ => "Finishing".to_string(),
            };
            let _ = on_progress.send(ProgressPayload {
                current,
                total: 100,
                message,
            });
            thread::sleep(Duration::from_millis(40));
        }
    });
    Ok(())
}
