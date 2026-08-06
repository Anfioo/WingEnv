export interface UpdateProgress {
  event: "Started" | "Progress" | "Finished";
  data?: {
    contentLength?: number;
    chunkLength?: number;
    downloaded?: number;
  };
}

export type UpdateInstallResult = "installed" | "cancelled" | "up-to-date";
