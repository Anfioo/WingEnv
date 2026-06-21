import { invoke } from "@tauri-apps/api/core";

export async function invokeCommand<TParams, TResult>(
  command: string,
  params: TParams
): Promise<TResult> {
  try {
    return await invoke<TResult>(command, params as Record<string, unknown>);
  } catch (error) {
    console.error("操作失败：", error);
    throw error;
  }
}
