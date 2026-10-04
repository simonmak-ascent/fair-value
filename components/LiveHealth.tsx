"use client";

import { useEffect, useState } from "react";

interface Health {
  status?: string;
  tool_count?: number;
  surface_version?: string;
  version?: string;
}

export function LiveHealth() {
  const [state, setState] = useState<"loading" | "ok" | "down">("loading");
  const [health, setHealth] = useState<Health | null>(null);

  useEffect(() => {
    let active = true;
    fetch("/v1/health", { headers: { accept: "application/json" } })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((data: Health) => {
        if (!active) return;
        setHealth(data);
        setState("ok");
      })
      .catch(() => active && setState("down"));
    return () => {
      active = false;
    };
  }, []);

  const dot =
    state === "ok" ? "bg-primary-500" : state === "down" ? "bg-secondary-400" : "bg-neutral-400";

  return (
    <span className="inline-flex items-center gap-2 rounded-md border border-neutral-200 px-2.5 py-1 text-[12px] dark:border-neutral-800">
      <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />
      <span className="text-neutral-600 dark:text-neutral-300">
        {state === "loading" && "checking /v1/health…"}
        {state === "ok" && `API live · ${health?.tool_count ?? "?"} tools`}
        {state === "down" && "API status unavailable"}
      </span>
    </span>
  );
}
