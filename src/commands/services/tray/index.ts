import { invokeCommand } from "../../base";
import type { UpdateTrayMenuParams, UpdateTrayMenuResult } from "./types";

export function updateTrayMenu(params: UpdateTrayMenuParams): Promise<UpdateTrayMenuResult> {
  return invokeCommand("update_tray_menu", params);
}
