import { Channel } from "@tauri-apps/api/core";
import { invokeCommand } from "../../base";
import type { UpdateInstallResult, UpdateProgress } from "./types";

export function downloadAndInstallUpdate(
  onProgress: (progress: UpdateProgress) => void
): Promise<UpdateInstallResult> {
  const channel = new Channel<UpdateProgress>();
  channel.onmessage = onProgress;
  return invokeCommand("download_and_install_update", { onProgress: channel });
}

export function cancelUpdateDownload(): Promise<boolean> {
  return invokeCommand("cancel_update_download", {});
}

export function isUpdateDownloadActive(): Promise<boolean> {
  return invokeCommand("is_update_download_active", {});
}

export type { UpdateInstallResult, UpdateProgress } from "./types";
