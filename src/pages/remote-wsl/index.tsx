import { AppPageContent } from "@/components/app-page-content";
import { AppShell } from "@/components/app-shell";
import { getAppRoute } from "@/lib/app-routes";

export default function RemoteWslPage() {
  return (
    <AppShell>
      <AppPageContent route={getAppRoute("remoteWsl")} />
    </AppShell>
  );
}
