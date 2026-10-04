"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { cn } from "@/lib/utils";
import type { Method } from "@/lib/catalog";
import { methods as allMethods } from "@/lib/catalog";

interface RunResult {
  status?: string;
  value?: number;
  method?: string;
  solution_type?: string;
  statistics?: { distribution?: string; sigma?: number; percentiles?: Record<string, number>; seed?: number | null };
  citations?: { ivs?: string[]; ifrs?: string[] };
  error?: string;
  [key: string]: unknown;
}

function parseValue(type: string, raw: string): unknown {
  const t = type.toLowerCase();
  if (t.includes("array")) {
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) return parsed;
    } catch {
      /* fall through */
    }
    return raw
      .split(/[,\s]+/)
      .filter(Boolean)
      .map((v) => Number(v));
  }
  if (t.includes("bool")) return raw === "true";
  if (t.includes("int")) return Math.trunc(Number(raw));
  if (t.includes("number")) return Number(raw);
  if (t.includes("object")) {
    try {
      return JSON.parse(raw);
    } catch {
      return {};
    }
  }
  return raw;
}

export function Playground() {
  const params = useSearchParams();
  const initial = params.get("method") ?? "dcf";
  const [methodId, setMethodId] = useState(initial);
  const [values, setValues] = useState<Record<string, string>>({});
  const [result, setResult] = useState<RunResult | null>(null);
  const [status, setStatus] = useState<"idle" | "running" | "error">("idle");

  const grouped = useMemo(() => {
    const map = new Map<string, Method[]>();
    for (const m of allMethods) {
      const arr = map.get(m.tool) ?? [];
      arr.push(m);
      map.set(m.tool, arr);
    }
    return map;
  }, []);

  const method = allMethods.find((m) => m.method === methodId);

  async function run() {
    if (!method) return;
    setStatus("running");
    setResult(null);
    const body: Record<string, unknown> = { method: method.method };
    for (const input of method.inputs) {
      const raw = values[input.name];
      if (raw === undefined || raw === "") continue;
      body[input.name] = parseValue(input.type, raw);
    }
    try {
      const res = await fetch(`/v1/calculate/${method.tool}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = (await res.json()) as RunResult;
      setResult(data);
      setStatus(res.ok ? "idle" : "error");
    } catch (e) {
      setResult({ error: e instanceof Error ? e.message : "request failed" });
      setStatus("error");
    }
  }

  const select =
    "rounded-md border border-neutral-300 bg-white px-2.5 py-1.5 text-[12.5px] dark:border-neutral-700 dark:bg-neutral-900";
  const field =
    "w-full rounded-md border border-neutral-300 bg-white px-2.5 py-1.5 font-mono text-[12.5px] dark:border-neutral-700 dark:bg-neutral-900";

  return (
    <div className="grid gap-5 lg:grid-cols-2">
      {/* Request */}
      <div className="flex flex-col gap-4">
        <label className="flex flex-col gap-1.5">
          <span className="text-[12px] font-medium uppercase tracking-wide muted">Method</span>
          <select
            value={methodId}
            onChange={(e) => {
              setMethodId(e.target.value);
              setValues({});
              setResult(null);
            }}
            className={select}
          >
            {Array.from(grouped.entries()).map(([tool, ms]) => (
              <optgroup key={tool} label={tool}>
                {ms.map((m) => (
                  <option key={m.method} value={m.method}>
                    {m.method}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </label>

        {method && (
          <>
            <p className="text-[13px] muted">{method.summary}</p>
            <div className="flex flex-col gap-3">
              {method.inputs.map((input) => (
                <label key={input.name} className="flex flex-col gap-1">
                  <span className="flex items-center gap-2 text-[12.5px]">
                    <span className="font-mono">{input.name}</span>
                    <span className="muted">{input.type}</span>
                    {method.required.includes(input.name) && (
                      <span className="text-secondary-500 dark:text-secondary-300">required</span>
                    )}
                  </span>
                  {input.type.includes("bool") ? (
                    <select
                      value={values[input.name] ?? ""}
                      onChange={(e) => setValues((v) => ({ ...v, [input.name]: e.target.value }))}
                      className={field}
                    >
                      <option value="">—</option>
                      <option value="true">true</option>
                      <option value="false">false</option>
                    </select>
                  ) : (
                    <textarea
                      rows={input.type.includes("array") || input.type.includes("object") ? 2 : 1}
                      value={values[input.name] ?? ""}
                      onChange={(e) => setValues((v) => ({ ...v, [input.name]: e.target.value }))}
                      placeholder={input.description}
                      className={field}
                    />
                  )}
                </label>
              ))}
            </div>
          </>
        )}

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={run}
            disabled={status === "running" || !method}
            className="rounded-md bg-primary-600 px-4 py-2 text-[13px] font-semibold text-white transition-colors hover:bg-primary-700 disabled:opacity-50"
          >
            {status === "running" ? "Running…" : "Run"}
          </button>
          {method && (
            <Link href={`/docs/methods/${method.method}`} className="text-[12.5px] muted hover:text-primary-600 dark:hover:text-primary-300">
              method reference →
            </Link>
          )}
        </div>
      </div>

      {/* Response */}
      <div className="flex flex-col gap-3">
        <span className="text-[12px] font-medium uppercase tracking-wide muted">Response</span>
        {result ? (
          <div className="flex flex-col gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone={result.status === "ok" ? "primary" : "gold"}>{result.status ?? "error"}</Badge>
              {result.solution_type && <Badge>{result.solution_type}</Badge>}
              {typeof result.value === "number" && (
                <span className="font-heading text-xl font-semibold tabular-nums">
                  {result.value.toLocaleString(undefined, { maximumFractionDigits: 6 })}
                </span>
              )}
            </div>
            {(result.citations?.ivs?.length || result.citations?.ifrs?.length) && (
              <div className="flex flex-wrap gap-1.5">
                {result.citations?.ivs?.map((id) => (
                  <Link key={id} href={`/docs/standards#${id}`}>
                    <Badge tone="primary">{id}</Badge>
                  </Link>
                ))}
                {result.citations?.ifrs?.map((id) => (
                  <Link key={id} href={`/docs/standards#${id}`}>
                    <Badge tone="gold">{id}</Badge>
                  </Link>
                ))}
              </div>
            )}
          </div>
        ) : (
          <p className="text-[13px] muted">Choose a method, fill the inputs, and run — the shared envelope appears here.</p>
        )}
        <pre className="scroll-thin max-h-[520px] overflow-auto rounded-md border border-neutral-200 bg-neutral-50 p-3 font-mono text-[12px] leading-relaxed dark:border-neutral-800 dark:bg-neutral-950">
          <code className={cn("text-neutral-800 dark:text-neutral-200")}>
            {result ? JSON.stringify(result, null, 2) : "// response"}
          </code>
        </pre>
      </div>
    </div>
  );
}
