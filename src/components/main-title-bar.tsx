import { Moon, Sun, Info, Settings } from "lucide-react";
import { useTheme } from "@/components/theme-provider";
import { createWindow } from "@/lib/window";
import { TitleBar } from "@/components/title-bar";
import { LanguageToggle } from "@/components/toggle/language-toggle";
import { useTranslation } from "react-i18next";
import { useUpdater } from "@/hooks/use-updater";

export function MainTitleBar() {
  const { theme, setTheme } = useTheme();
  const { t } = useTranslation();
  const { hasUpdate, availableVersion } = useUpdater();

  const handleToggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  const handleOpenAbout = async () => {
    await createWindow("about", {
      title: t("about.title"),
      url: "/about",
      width: 500,
      height: 400,
      resizable: false,
      maximizable: false,
      minimizable: false,
      decorations: false,
      transparent: true,
      shadow: false,
      alwaysOnTop: true,
      parent: "main",
    });
  };

  const handleOpenSettings = async () => {
    await createWindow("settings", {
      title: t("settings.title"),
      url: "/settings",
      width: 600,
      height: 500,
      resizable: true,
      maximizable: true,
      minimizable: false,
      decorations: false,
      transparent: true,
      shadow: false,
      parent: "main",
    });
  };

  return (
    <TitleBar
      title={t("app.title")}
      rightActions={
        <>
          <button
            onClick={handleOpenSettings}
            className="title-bar-btn mr-1"
            aria-label={t("settings.button")}
            tabIndex={-1}
          >
            <Settings className="h-4 w-4" />
          </button>

          <button
            onClick={handleOpenAbout}
            className="title-bar-btn relative mr-1"
            aria-label={t("about.button")}
            title={
              hasUpdate
                ? t("updater.versionAvailable", { version: availableVersion })
                : t("about.button")
            }
            tabIndex={-1}
          >
            <Info className="h-4 w-4" />
            {hasUpdate && (
              <span
                className="bg-destructive ring-background absolute top-1 right-1 size-1.5 rounded-full ring-2"
                aria-hidden="true"
              />
            )}
          </button>

          <LanguageToggle />

          <button
            onClick={handleToggleTheme}
            className="title-bar-btn mr-0.5"
            aria-label={t("theme.toggle")}
            tabIndex={-1}
          >
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
        </>
      }
    />
  );
}
