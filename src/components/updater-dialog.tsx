import { useCallback, useEffect, useRef, useState } from "react";
import { useUpdater } from "@/hooks/use-updater";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { XIcon } from "lucide-react";

const AUTO_CHECK_SESSION_KEY = "wingenv-updater-auto-check-started";

interface UpdaterDialogProps {
  autoCheck?: boolean;
}

export function UpdaterDialog({ autoCheck = false }: UpdaterDialogProps) {
  const {
    update,
    availableVersion,
    downloading,
    cancelling,
    updateDialogOpen,
    progress,
    checkUpdate,
    installUpdate,
    cancelDownload,
    dismissUpdate,
    hideUpdateDialog,
  } = useUpdater();
  const didAutoCheck = useRef(false);
  const { t } = useTranslation();

  useEffect(() => {
    if (
      !autoCheck ||
      didAutoCheck.current ||
      downloading ||
      sessionStorage.getItem(AUTO_CHECK_SESSION_KEY) === "true"
    ) {
      return;
    }

    didAutoCheck.current = true;
    sessionStorage.setItem(AUTO_CHECK_SESSION_KEY, "true");
    void checkUpdate().then((result) => {
      if (result.status === "error") {
        toast.error(t("updater.checkFailed"));
      }
    });
  }, [autoCheck, checkUpdate, downloading, t]);

  const handleInstall = async () => {
    try {
      await installUpdate();
    } catch (error) {
      console.error("Failed to install update:", error);
      toast.error(t("updater.installFailed"));
    }
  };

  const handleCancelDownload = async () => {
    try {
      if (await cancelDownload()) {
        toast.info(t("updater.downloadCancelled"));
      }
    } catch (error) {
      console.error("Failed to cancel update download:", error);
      toast.error(t("updater.cancelFailed"));
    }
  };

  const installing = progress?.event === "Finished";

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      hideUpdateDialog();
    }
  };

  const getProgressPercentage = () => {
    if (!progress || progress.event === "Started") return 0;
    const { downloaded, contentLength } = progress.data || {};
    if (!contentLength) return 0;
    if (progress.event === "Finished") return 100;
    return Math.round(((downloaded ?? 0) / contentLength) * 100);
  };

  return (
    <Dialog
      open={Boolean(update || downloading) && updateDialogOpen}
      onOpenChange={handleOpenChange}
    >
      <DialogContent showCloseButton={!installing}>
        <DialogHeader>
          <DialogTitle>
            {downloading ? t("updater.downloading") : t("updater.updateAvailable")}
          </DialogTitle>
          <DialogDescription>
            {downloading
              ? t("updater.installingVersion", { version: update?.version ?? availableVersion })
              : t("updater.versionAvailable", { version: update?.version ?? availableVersion })}
          </DialogDescription>
        </DialogHeader>
        {downloading ? (
          <Progress value={getProgressPercentage()} />
        ) : (
          update?.body && (
            <div className="bg-muted flex flex-col gap-1 rounded-md p-3 text-sm">
              <p className="font-semibold">{t("updater.releaseNotes")}</p>
              <p className="text-muted-foreground whitespace-pre-wrap">{update.body}</p>
            </div>
          )
        )}
        {downloading && !installing ? (
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => void handleCancelDownload()}
              disabled={cancelling}
            >
              <XIcon data-icon="inline-start" />
              {cancelling ? t("updater.cancelling") : t("updater.cancelDownload")}
            </Button>
          </DialogFooter>
        ) : !downloading ? (
          <DialogFooter>
            <Button variant="outline" onClick={dismissUpdate}>
              {t("updater.later")}
            </Button>
            <Button onClick={() => void handleInstall()}>{t("updater.installNow")}</Button>
          </DialogFooter>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}

export function useManualUpdateCheck() {
  const { checkUpdate, checking, downloading, showUpdateDialog } = useUpdater();
  const [showNoUpdate, setShowNoUpdate] = useState(false);
  const { t } = useTranslation();

  const handleCheckUpdate = useCallback(async () => {
    setShowNoUpdate(false);

    if (downloading) {
      showUpdateDialog();
      return;
    }

    const result = await checkUpdate();

    if (result.status === "up-to-date") {
      setShowNoUpdate(true);
      return;
    }

    if (result.status === "disabled") {
      toast.info(t("updater.disabledInDev"));
      return;
    }

    if (result.status === "error") {
      toast.error(t("updater.checkFailed"));
    }
  }, [checkUpdate, downloading, showUpdateDialog, t]);

  return {
    checkUpdate: handleCheckUpdate,
    checking,
    downloading,
    showNoUpdate,
    dismissNoUpdate: () => setShowNoUpdate(false),
  };
}
