import { useState } from "react";
import { greet } from "@/commands";
import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getAppRoute } from "@/lib/app-routes";

export default function PrivateRegistryPage() {
  const route = getAppRoute("privateRegistry");
  const Icon = route.icon;
  const [name, setName] = useState("");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmedName = name.trim();
    if (!trimmedName) {
      setMessage("Please enter a name first.");
      return;
    }

    setSubmitting(true);
    try {
      const result = await greet({ name: trimmedName });
      setMessage(result);
    } catch (error) {
      console.error("Failed to call greet command:", error);
      setMessage("Failed to call Rust backend.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppShell>
      <section className="mx-auto flex w-full max-w-3xl flex-col gap-6">
        <div className="border-border bg-card text-card-foreground rounded-xl border p-6 shadow-sm">
          <div className="flex items-start gap-4">
            <div className="bg-primary text-primary-foreground flex size-11 shrink-0 items-center justify-center rounded-xl">
              <Icon className="size-5" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-muted-foreground text-sm">{route.scope}</p>
              <h2 className="mt-1 text-2xl font-semibold tracking-tight">{route.title}</h2>
              <p className="text-muted-foreground mt-2 max-w-2xl text-sm leading-6">
                输入一段文字并发送到 Rust 后端，通过 Tauri command 返回 greet 调用结果。
              </p>
            </div>
          </div>
        </div>

        <div className="border-border bg-card rounded-xl border p-6 shadow-sm">
          <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <label htmlFor="greet-name" className="text-sm font-medium">
                打招呼内容
              </label>
              <Input
                id="greet-name"
                value={name}
                onChange={(event) => setName(event.currentTarget.value)}
                placeholder="例如 WingEnv"
                disabled={submitting}
              />
            </div>

            <div className="flex items-center gap-3">
              <Button type="submit" disabled={submitting}>
                {submitting ? "发送中..." : "发送到 Rust 后端"}
              </Button>
              <Button
                type="button"
                variant="outline"
                disabled={submitting || (!name && !message)}
                onClick={() => {
                  setName("");
                  setMessage("");
                }}
              >
                清空
              </Button>
            </div>
          </form>

          {message && (
            <div className="bg-muted text-muted-foreground mt-5 rounded-lg p-4 text-sm">
              <p className="text-foreground mb-1 font-medium">Rust 返回结果</p>
              <p>{message}</p>
            </div>
          )}
        </div>
      </section>
    </AppShell>
  );
}
