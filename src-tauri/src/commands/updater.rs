use std::sync::Mutex;

use futures_util::{
    future::{select, Either},
    pin_mut,
};
use serde::Serialize;
use tauri::{ipc::Channel, AppHandle, State};
use tauri_plugin_updater::UpdaterExt;
use tokio::sync::watch;

#[derive(Default)]
pub struct UpdateDownloadState {
    cancel: Mutex<Option<watch::Sender<bool>>>,
}

#[derive(Clone, Serialize)]
#[serde(tag = "event", content = "data")]
pub enum UpdateProgressEvent {
    Started {
        #[serde(rename = "contentLength")]
        content_length: Option<u64>,
    },
    Progress {
        #[serde(rename = "chunkLength")]
        chunk_length: usize,
    },
    Finished,
}

#[derive(Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum UpdateInstallResult {
    Installed,
    Cancelled,
    UpToDate,
}

async fn run_update(
    app: &AppHandle,
    on_progress: Channel<UpdateProgressEvent>,
    mut cancel: watch::Receiver<bool>,
) -> Result<UpdateInstallResult, String> {
    let updater = app.updater().map_err(|error| error.to_string())?;
    let update = {
        let cancelled = cancel.changed();
        let check = updater.check();
        pin_mut!(cancelled, check);
        match select(cancelled, check).await {
            Either::Left(_) => return Ok(UpdateInstallResult::Cancelled),
            Either::Right((result, _)) => result.map_err(|error| error.to_string())?,
        }
    };

    let Some(update) = update else {
        return Ok(UpdateInstallResult::UpToDate);
    };

    let mut started = false;
    let download = update.download(
        |chunk_length, content_length| {
            if !started {
                started = true;
                let _ = on_progress.send(UpdateProgressEvent::Started { content_length });
            }
            let _ = on_progress.send(UpdateProgressEvent::Progress { chunk_length });
        },
        || {
            let _ = on_progress.send(UpdateProgressEvent::Finished);
        },
    );
    tokio::pin!(download);

    let bytes = {
        let cancelled = cancel.changed();
        pin_mut!(cancelled, download);
        match select(cancelled, download).await {
            Either::Left(_) => return Ok(UpdateInstallResult::Cancelled),
            Either::Right((result, _)) => result.map_err(|error| error.to_string())?,
        }
    };

    update.install(bytes).map_err(|error| error.to_string())?;
    Ok(UpdateInstallResult::Installed)
}

#[tauri::command]
pub async fn download_and_install_update(
    app: AppHandle,
    state: State<'_, UpdateDownloadState>,
    on_progress: Channel<UpdateProgressEvent>,
) -> Result<UpdateInstallResult, String> {
    let (cancel_sender, cancel_receiver) = watch::channel(false);
    {
        let mut active = state
            .cancel
            .lock()
            .map_err(|_| "Update download state is unavailable".to_string())?;
        if active.is_some() {
            return Err("An update download is already running".to_string());
        }
        *active = Some(cancel_sender);
    }

    let result = run_update(&app, on_progress, cancel_receiver).await;
    state
        .cancel
        .lock()
        .map_err(|_| "Update download state is unavailable".to_string())?
        .take();
    result
}

#[tauri::command]
pub fn cancel_update_download(state: State<'_, UpdateDownloadState>) -> Result<bool, String> {
    let active = state
        .cancel
        .lock()
        .map_err(|_| "Update download state is unavailable".to_string())?;
    Ok(active
        .as_ref()
        .is_some_and(|cancel_sender| cancel_sender.send(true).is_ok()))
}

#[tauri::command]
pub fn is_update_download_active(state: State<'_, UpdateDownloadState>) -> Result<bool, String> {
    let active = state
        .cancel
        .lock()
        .map_err(|_| "Update download state is unavailable".to_string())?;
    Ok(active.is_some())
}
