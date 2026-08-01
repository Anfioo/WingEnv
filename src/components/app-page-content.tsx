import type { AppRoute } from "@/lib/app-routes";

type AppPageContentProps = {
  route: AppRoute;
};

export function AppPageContent({ route }: AppPageContentProps) {
  const Icon = route.icon;

  return (
    <section className="mx-auto flex w-full max-w-5xl flex-col gap-6">
      <div className="border-border bg-card text-card-foreground rounded-xl border p-6 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="bg-primary text-primary-foreground flex size-11 shrink-0 items-center justify-center rounded-xl">
            <Icon className="size-5" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-muted-foreground text-sm">{route.scope}</p>
            <h2 className="mt-1 text-2xl font-semibold tracking-tight">{route.title}</h2>
            <p className="text-muted-foreground mt-2 max-w-2xl text-sm leading-6">
              {route.description}
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {route.items.map((item) => (
          <div key={item} className="border-border bg-card rounded-xl border p-4 shadow-sm">
            <div className="bg-muted mb-3 flex size-8 items-center justify-center rounded-lg">
              <Icon className="size-4" />
            </div>
            <h3 className="text-sm font-medium">{item}</h3>
            <p className="text-muted-foreground mt-2 text-xs leading-5">
              后续功能模块将在这里接入实际数据和操作。
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
