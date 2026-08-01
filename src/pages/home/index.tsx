import { AppPageContent } from "@/components/app-page-content";
import { AppShell } from "@/components/app-shell";
import { getAppRoute } from "@/lib/app-routes";

export default function HomePage() {
  return (
    <AppShell>
      <AppPageContent route={getAppRoute("overview")} />
    </AppShell>
  );
}
