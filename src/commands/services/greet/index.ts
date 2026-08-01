import { invokeCommand } from "../../base";
import type { GreetParams, GreetResult } from "./types";

export function greet(params: GreetParams): Promise<GreetResult> {
  return invokeCommand("greet", params);
}
