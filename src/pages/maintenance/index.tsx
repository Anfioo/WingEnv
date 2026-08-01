import { AppPageContent } from "@/components/app-page-content";
import { AppShell } from "@/components/app-shell";
import { getAppRoute } from "@/lib/app-routes";

export default function MaintenancePage() {
  return (
    <AppShell>
      <AppPageContent route={getAppRoute("maintenance")} />
    </AppShell>
  );
}
