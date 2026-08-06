import { useEffect, type ReactNode } from "react";
import { updateTrayMenu } from "@/commands/services/tray";
import { AppSidebar } from "@/components/app-sidebar";
import { MainTitleBar } from "@/components/main-title-bar";
import { UpdaterDialog } from "@/components/updater-dialog";
import { WindowFrame } from "@/components/window-frame";
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { ecosystemRoutes, getAppRouteByPath, workspaceRoutes } from "@/lib/app-routes";
import { registerShortcut } from "@/lib/shortcut";
import { toggleWindow } from "@/lib/window";
import { listen } from "@tauri-apps/api/event";
import { useAppTranslation } from "@/hooks/use-app-translation";

const SHORTCUT_KEY = "global-shortcut-show-main";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  const { t } = useAppTranslation();
  const currentRoute = getAppRouteByPath(window.location.pathname);
  const CurrentIcon = currentRoute.icon;

  useEffect(() => {
    const unlistenShortcutChanged = listen<{ shortcut: string }>(
      "shortcut-changed",
      async (event) => {
        console.log("Shortcut changed event received:", event.payload.shortcut);
        const newShortcut = event.payload.shortcut;
        if (newShortcut) {
          await registerShortcut(newShortcut, async () => {
            await toggleWindow("main");
          });
        }
      }
    );

    const initTrayMenu = async () => {
      try {
        await updateTrayMenu({
          showText: t("tray.show"),
          quitText: t("tray.quit"),
        });
      } catch (error) {
        console.error("Failed to initialize tray menu:", error);
      }
    };
    initTrayMenu();

    const initShortcut = async () => {
      const savedShortcut = localStorage.getItem(SHORTCUT_KEY);
      if (savedShortcut) {
        console.log("Registering saved shortcut:", savedShortcut);
        await registerShortcut(savedShortcut, async () => {
          await toggleWindow("main");
        });
      }
    };
    initShortcut();

    return () => {
      unlistenShortcutChanged.then((fn) => fn());
    };
  }, [t]);

  return (
    <WindowFrame titleBar={<MainTitleBar />} contentClassName="flex flex-1 overflow-hidden">
      <UpdaterDialog autoCheck />
      <SidebarProvider className="min-h-0 flex-1">
        <AppSidebar
          workspaceRoutes={workspaceRoutes}
          ecosystemRoutes={ecosystemRoutes}
          activePath={currentRoute.path}
        />
        <SidebarInset className="min-w-0 overflow-hidden">
          <header className="border-border flex h-12 shrink-0 items-center gap-3 border-b px-4">
            <SidebarTrigger />
            <div className="bg-muted flex size-7 items-center justify-center rounded-md">
              <CurrentIcon className="size-4" />
            </div>
            <div className="min-w-0">
              <h1 className="truncate text-sm font-semibold">{currentRoute.title}</h1>
              <p className="text-muted-foreground truncate text-xs">{currentRoute.scope}</p>
            </div>
          </header>

          <main className="flex min-h-0 flex-1 overflow-auto p-6">{children}</main>
        </SidebarInset>
      </SidebarProvider>
    </WindowFrame>
  );
}
