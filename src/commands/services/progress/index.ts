import { Channel } from "@tauri-apps/api/core";
import { invokeCommand } from "../../base";
import type { ProgressPayload } from "./types";

export function runProgressDemo(onProgress: (payload: ProgressPayload) => void): Promise<void> {
  const channel = new Channel<ProgressPayload>();
  channel.onmessage = onProgress;
  return invokeCommand("run_progress_demo", { onProgress: channel });
}
