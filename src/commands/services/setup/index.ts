import { invokeCommand } from "../../base";
import type { SetCompleteParams, SetCompleteResult } from "./types";

export function setComplete(params: SetCompleteParams): Promise<SetCompleteResult> {
  return invokeCommand("set_complete", params);
}
