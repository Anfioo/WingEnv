import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import "./i18n";
import HomePage from "./pages/home/index";
import StorePage from "./pages/store/index";
import VersionsPage from "./pages/versions/index";
import MaintenancePage from "./pages/maintenance/index";
import EnvironmentSettingsPage from "./pages/environment-settings/index";
import RemoteWslPage from "./pages/remote-wsl/index";
import ContainersPage from "./pages/containers/index";
import PrivateRegistryPage from "./pages/private-registry/index";
import AboutPage from "./windows/about/index";
import SettingsPage from "./windows/settings/index";

const pageMap = {
  "/": HomePage,
  "/store": StorePage,
  "/versions": VersionsPage,
  "/maintenance": MaintenancePage,
  "/environment-settings": EnvironmentSettingsPage,
  "/remote-wsl": RemoteWslPage,
  "/containers": ContainersPage,
  "/private-registry": PrivateRegistryPage,
  "/about": AboutPage,
  "/settings": SettingsPage,
};

const pathname = window.location.pathname;
const PageComponent = pageMap[pathname as keyof typeof pageMap] ?? HomePage;

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <PageComponent />
  </React.StrictMode>
);
