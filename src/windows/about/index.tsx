import { useEffect, useState } from "react";
import { getVersion } from "@tauri-apps/api/app";
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";
import { CircleArrowUp, Github, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button.tsx";
import { TitleBar } from "@/components/title-bar.tsx";
import { WindowFrame } from "@/components/window-frame.tsx";
import { useAppTranslation } from "@/hooks/use-app-translation.ts";
import { openUrl } from "@tauri-apps/plugin-opener";
import { cancelDestroyWindow, destroyWindow } from "@/lib/window.ts";
import { UpdaterDialog, useManualUpdateCheck } from "@/components/updater-dialog.tsx";
import packageJson from "../../../package.json";
import { useUpdater } from "@/hooks/use-updater";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

const techVersions = {
  tauri: packageJson.dependencies["@tauri-apps/api"].replace(/^\^/, "v"),
  react: packageJson.dependencies.react.replace(/^\^/, "v"),
  typescript: packageJson.devDependencies.typescript.replace(/^~/, "v"),
};

export default function AboutPage() {
  const [appVersion, setAppVersion] = useState("");
  const { t } = useAppTranslation();
  const { checkUpdate, checking, downloading, showNoUpdate } = useManualUpdateCheck();
  const { availableVersion } = useUpdater();

  useEffect(() => {
    void getVersion().then(setAppVersion);
  }, []);

  useEffect(() => {
    const appWindow = getCurrentWebviewWindow();

    const unlistenClose = appWindow.onCloseRequested(async (event) => {
      event.preventDefault();
      console.log("About window close requested, will destroy in 5 seconds");
      await destroyWindow(appWindow.label, 5000);
    });

    const unlistenFocusChanged = appWindow.onFocusChanged(({ payload: focused }) => {
      if (focused) {
        cancelDestroyWindow(appWindow.label);
      }
    });

    return () => {
      unlistenClose.then((fn) => fn());
      unlistenFocusChanged.then((fn) => fn());
    };
  }, []);

  const handleOpenGithub = async () => {
    await openUrl("https://github.com/anfioo/wingenv");
  };

  return (
    <WindowFrame
      titleBar={<TitleBar title={t("about.title")} showMinimize={false} showMaximize={false} />}
      contentClassName="flex flex-1 items-center justify-center overflow-hidden"
    >
      <UpdaterDialog />
      <div className="w-full max-w-xs space-y-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold">{t("about.appName")}</h2>
        </div>

        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">{t("about.version")}</span>
            <span className="flex items-center gap-1.5 font-medium">
              {appVersion}
              {availableVersion && (
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <CircleArrowUp
                        className="text-destructive size-4"
                        aria-label={t("updater.versionAvailable", { version: availableVersion })}
                      />
                    </TooltipTrigger>
                    <TooltipContent>
                      {t("updater.versionAvailable", { version: availableVersion })}
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              )}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Tauri</span>
            <span className="font-medium">{techVersions.tauri}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">React</span>
            <span className="font-medium">{techVersions.react}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">TypeScript</span>
            <span className="font-medium">{techVersions.typescript}</span>
          </div>
        </div>

        <Button onClick={handleOpenGithub} className="w-full" variant="outline">
          <Github className="mr-2 h-4 w-4" />
          GitHub
        </Button>

        <Button onClick={checkUpdate} className="w-full" variant="outline" disabled={checking}>
          <RefreshCw
            data-icon="inline-start"
            className={checking || downloading ? "animate-spin" : undefined}
          />
          {checking
            ? t("updater.checking")
            : downloading
              ? t("updater.updating")
              : t("updater.checkForUpdates")}
        </Button>

        {showNoUpdate && (
          <p className="text-muted-foreground text-center text-sm">{t("updater.upToDate")}</p>
        )}
      </div>
    </WindowFrame>
  );
}
