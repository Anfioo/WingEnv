import { useState, useEffect } from "react";
import { updateTrayMenu } from "@/commands/services/tray";
import { WindowFrame } from "@/components/window-frame";
import { MainTitleBar } from "@/components/main-title-bar";
import { UpdaterDialog } from "@/components/updater-dialog";
import { listen } from "@tauri-apps/api/event";
import { registerShortcut } from "@/lib/shortcut";
import { toggleWindow } from "@/lib/window";
import { useAppTranslation } from "@/hooks/use-app-translation";
import { cn } from "@/lib/utils";
import { Home, TestTube2 } from "lucide-react";
import WelcomePage from "./welcome";
import TestPage from "./test";

const SHORTCUT_KEY = "global-shortcut-show-main";

type PageSection = "home" | "test" | "settings";

export default function HomePage() {
  const [activeSection, setActiveSection] = useState<PageSection>("home");
  const { t } = useAppTranslation();

  useEffect(() => {
    // Listen for shortcut change events from settings window
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

    // Initialize tray menu with current language
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

    // Register global shortcut on app startup
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

  const menuItems = [
    {
      id: "home" as PageSection,
      label: t("app.welcome"),
      icon: Home,
    },
    {
      id: "test" as PageSection,
      label: "Test",
      icon: TestTube2,
    },
  ];

  return (
    <WindowFrame titleBar={<MainTitleBar />} contentClassName="flex flex-1 overflow-hidden">
      <UpdaterDialog />
      <aside className="border-border flex w-40 flex-col border-r p-4">
        <nav className="flex-1 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={cn(
                  "flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                  activeSection === item.id
                    ? "bg-accent text-accent-foreground font-medium"
                    : "text-muted-foreground hover:bg-accent/50 hover:text-foreground"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </button>
            );
          })}
        </nav>
      </aside>

      <div className="flex-1 overflow-auto">
        {activeSection === "home" && <WelcomePage />}
        {activeSection === "test" && <TestPage />}
      </div>
    </WindowFrame>
  );
}
