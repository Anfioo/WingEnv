import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { cancelUpdateDownload, downloadAndInstallUpdate, isUpdateDownloadActive } from "@/commands";
import type { UpdateInstallResult, UpdateProgress } from "@/commands";
import { checkForUpdates } from "@/lib/updater";
import type { UpdateCheckResult } from "@/lib/updater";
import { relaunch } from "@tauri-apps/plugin-process";
import type { Update } from "@tauri-apps/plugin-updater";

const AVAILABLE_VERSION_STORAGE_KEY = "wingenv-updater-available-version";
const DOWNLOAD_ACTIVE_STORAGE_KEY = "wingenv-updater-download-active";
const DOWNLOAD_PROGRESS_STORAGE_KEY = "wingenv-updater-download-progress";

function readStoredProgress(): UpdateProgress | null {
  const value = localStorage.getItem(DOWNLOAD_PROGRESS_STORAGE_KEY);
  if (!value) return null;

  try {
    return JSON.parse(value) as UpdateProgress;
  } catch {
    localStorage.removeItem(DOWNLOAD_PROGRESS_STORAGE_KEY);
    return null;
  }
}

interface UpdaterContextValue {
  update: Update | null;
  availableVersion: string | null;
  hasUpdate: boolean;
  checking: boolean;
  downloading: boolean;
  cancelling: boolean;
  updateDialogOpen: boolean;
  progress: UpdateProgress | null;
  checkUpdate: () => Promise<UpdateCheckResult>;
  installUpdate: () => Promise<UpdateInstallResult | null>;
  cancelDownload: () => Promise<boolean>;
  dismissUpdate: () => void;
  showUpdateDialog: () => void;
  hideUpdateDialog: () => void;
}

const UpdaterContext = createContext<UpdaterContextValue | null>(null);

export function UpdaterProvider({ children }: { children: ReactNode }) {
  const [update, setUpdate] = useState<Update | null>(null);
  const [availableVersion, setAvailableVersion] = useState<string | null>(() =>
    localStorage.getItem(AVAILABLE_VERSION_STORAGE_KEY)
  );
  const [checking, setChecking] = useState(false);
  const [downloading, setDownloading] = useState(
    () => localStorage.getItem(DOWNLOAD_ACTIVE_STORAGE_KEY) === "true"
  );
  const [cancelling, setCancelling] = useState(false);
  const [updateDialogOpen, setUpdateDialogOpen] = useState(false);
  const [progress, setProgress] = useState<UpdateProgress | null>(readStoredProgress);
  const pendingCheck = useRef<Promise<UpdateCheckResult> | null>(null);

  useEffect(() => {
    const handleStorage = (event: StorageEvent) => {
      if (event.key === AVAILABLE_VERSION_STORAGE_KEY) {
        setAvailableVersion(event.newValue);
      } else if (event.key === DOWNLOAD_ACTIVE_STORAGE_KEY) {
        setDownloading(event.newValue === "true");
      } else if (event.key === DOWNLOAD_PROGRESS_STORAGE_KEY) {
        setProgress(readStoredProgress());
      }
    };

    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, []);

  const storeAvailableVersion = useCallback((version: string | null) => {
    setAvailableVersion(version);
    if (version) {
      localStorage.setItem(AVAILABLE_VERSION_STORAGE_KEY, version);
    } else {
      localStorage.removeItem(AVAILABLE_VERSION_STORAGE_KEY);
    }
  }, []);

  const storeDownloading = useCallback((active: boolean) => {
    setDownloading(active);
    if (active) {
      localStorage.setItem(DOWNLOAD_ACTIVE_STORAGE_KEY, "true");
    } else {
      localStorage.removeItem(DOWNLOAD_ACTIVE_STORAGE_KEY);
    }
  }, []);

  const storeProgress = useCallback((nextProgress: UpdateProgress | null) => {
    setProgress(nextProgress);
    if (nextProgress) {
      localStorage.setItem(DOWNLOAD_PROGRESS_STORAGE_KEY, JSON.stringify(nextProgress));
    } else {
      localStorage.removeItem(DOWNLOAD_PROGRESS_STORAGE_KEY);
    }
  }, []);

  useEffect(() => {
    void isUpdateDownloadActive()
      .then(storeDownloading)
      .catch((error) => console.error("Failed to read update download status:", error));
  }, [storeDownloading]);

  const checkUpdate = useCallback((): Promise<UpdateCheckResult> => {
    if (pendingCheck.current) {
      return pendingCheck.current;
    }

    setChecking(true);
    const request = checkForUpdates();
    pendingCheck.current = request;

    void request
      .then((result) => {
        if (result.status === "available") {
          setUpdate(result.update);
          setUpdateDialogOpen(true);
          storeAvailableVersion(result.update.version);
        } else if (result.status === "up-to-date") {
          setUpdate(null);
          setUpdateDialogOpen(false);
          storeAvailableVersion(null);
        }
        storeProgress(null);
      })
      .finally(() => {
        pendingCheck.current = null;
        setChecking(false);
      });

    return request;
  }, [storeAvailableVersion, storeProgress]);

  const handleProgress = useCallback((event: UpdateProgress) => {
    setProgress((current) => {
      let next: UpdateProgress;
      if (event.event === "Started") {
        next = { ...event, data: { ...event.data, downloaded: 0 } };
      } else if (event.event === "Progress") {
        next = {
          ...event,
          data: {
            ...event.data,
            contentLength: current?.data?.contentLength,
            downloaded: (current?.data?.downloaded ?? 0) + (event.data?.chunkLength ?? 0),
          },
        };
      } else {
        next = {
          ...event,
          data: {
            contentLength: current?.data?.contentLength,
            downloaded: current?.data?.downloaded,
          },
        };
      }

      localStorage.setItem(DOWNLOAD_PROGRESS_STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  }, []);

  const installUpdate = useCallback(async () => {
    if (!update || downloading) {
      return null;
    }

    storeDownloading(true);
    storeProgress(null);
    try {
      const result = await downloadAndInstallUpdate(handleProgress);
      if (result === "installed") {
        storeAvailableVersion(null);
        await relaunch();
      } else if (result === "up-to-date") {
        setUpdate(null);
        setUpdateDialogOpen(false);
        storeAvailableVersion(null);
      } else {
        storeProgress(null);
      }
      return result;
    } finally {
      storeDownloading(false);
      setCancelling(false);
    }
  }, [downloading, handleProgress, storeAvailableVersion, storeDownloading, storeProgress, update]);

  const cancelDownload = useCallback(async () => {
    if (!downloading || cancelling) {
      return false;
    }

    setCancelling(true);
    try {
      return await cancelUpdateDownload();
    } finally {
      setCancelling(false);
    }
  }, [cancelling, downloading]);

  const dismissUpdate = useCallback(() => {
    if (!downloading) {
      setUpdate(null);
      storeProgress(null);
      setUpdateDialogOpen(false);
    }
  }, [downloading, storeProgress]);

  const showUpdateDialog = useCallback(() => {
    if (update || downloading) {
      setUpdateDialogOpen(true);
    }
  }, [downloading, update]);

  const hideUpdateDialog = useCallback(() => {
    setUpdateDialogOpen(false);
  }, []);

  const value = useMemo(
    () => ({
      update,
      availableVersion,
      hasUpdate: availableVersion !== null,
      checking,
      downloading,
      cancelling,
      updateDialogOpen,
      progress,
      checkUpdate,
      installUpdate,
      cancelDownload,
      dismissUpdate,
      showUpdateDialog,
      hideUpdateDialog,
    }),
    [
      update,
      availableVersion,
      checking,
      downloading,
      cancelling,
      updateDialogOpen,
      progress,
      checkUpdate,
      installUpdate,
      cancelDownload,
      dismissUpdate,
      showUpdateDialog,
      hideUpdateDialog,
    ]
  );

  return <UpdaterContext.Provider value={value}>{children}</UpdaterContext.Provider>;
}

export function useUpdater() {
  const context = useContext(UpdaterContext);
  if (!context) {
    throw new Error("useUpdater must be used inside UpdaterProvider");
  }

  return context;
}
