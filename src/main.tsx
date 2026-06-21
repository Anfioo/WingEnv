import React, { lazy, Suspense, useEffect } from "react";
import ReactDOM from "react-dom/client";
import { invoke } from "@tauri-apps/api/core";
import "./index.css";
import "./i18n";

const HomePage = lazy(() => import("./pages/home"));
const AboutPage = lazy(() => import("./pages/about"));
const SettingsPage = lazy(() => import("./pages/settings"));

const pageMap = {
  "/": HomePage,
  "/about": AboutPage,
  "/settings": SettingsPage,
};

const pathname = window.location.pathname;
const PageComponent = pageMap[pathname as keyof typeof pageMap] ?? HomePage;

function sleep(seconds: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, seconds * 1000));
}

async function setup() {
  console.log("Performing really heavy frontend setup task...");
  await sleep(3);
  console.log("Frontend setup task complete!");
  invoke("set_complete", { task: "frontend" });
}

function AppWrapper() {
  useEffect(() => {
    setup();
  }, []);

  return <PageComponent />;
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <Suspense fallback={null}>
      <AppWrapper />
    </Suspense>
  </React.StrictMode>
);
