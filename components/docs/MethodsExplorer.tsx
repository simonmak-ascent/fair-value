"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { methods as allMethods, tools } from "@/lib/catalog";
import { cn } from "@/lib/utils";

export function MethodsExplorer() {
  const [q, setQ] = useState("");
  const [tool, setTool] = useState("");
  const [approach, setApproach] = useState("");

  const approaches = useMemo(
    () => Array.from(new Set(allMethods.map((m) => m.approach))).sort(),
    [],
  );

  const rows = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return allMethods.filter((m) => {
      if (tool && m.tool !== tool) return false;
      if (approach && m.approach !== approach) return false;
      if (!needle) return true;
      return (
        m.method.toLowerCase().includes(needle) ||
        m.summary.toLowerCase().includes(needle) ||
        m.formula_ref.toLowerCase().includes(needle) ||
        m.citations.some((c) => c.id.toLowerCase().includes(needle))
      );
    });
  }, [q, tool, approach]);

  const select =
    "rounded-md border border-neutral-300 bg-white px-2.5 py-1.5 text-[12.5px] dark:border-neutral-700 dark:bg-neutral-900";

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search methods, summaries, clauses…"
          className={cn(select, "w-full sm:w-72")}
          aria-label="Search methods"
        />
        <select value={tool} onChange={(e) => setTool(e.target.value)} className={select} aria-label="Filter by tool">
          <option value="">All tools</option>
          {tools.map((t) => (
            <option key={t.id} value={t.id}>
              {t.id}
            </option>
          ))}
        </select>
        <select
          value={approach}
          onChange={(e) => setApproach(e.target.value)}
          className={select}
          aria-label="Filter by approach"
        >
          <option value="">All approaches</option>
          {approaches.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
        <span className="ml-auto text-[12.5px] muted">{rows.length} / {allMethods.length}</span>
      </div>

      <div className="overflow-x-auto rounded-md border border-neutral-200 dark:border-neutral-800">
        <table className="w-full min-w-[720px] border-collapse text-[13px]">
          <thead>
            <tr className="border-b border-neutral-200 bg-neutral-50 text-left dark:border-neutral-800 dark:bg-neutral-900">
              <th className="px-3 py-2 font-medium">Method</th>
              <th className="px-3 py-2 font-medium">Tool</th>
              <th className="px-3 py-2 font-medium">Approach</th>
              <th className="px-3 py-2 font-medium">Type</th>
              <th className="px-3 py-2 font-medium">Clauses</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((m) => (
              <tr
                key={m.method}
                className="border-b border-neutral-100 last:border-0 hover:bg-neutral-50 dark:border-neutral-900 dark:hover:bg-neutral-900/60"
              >
                <td className="px-3 py-2">
                  <Link
                    href={`/docs/methods/${m.method}`}
                    className="font-mono text-[12.5px] text-primary-700 hover:underline dark:text-primary-300"
                  >
                    {m.method}
                  </Link>
                  {!m.implemented && (
                    <span className="ml-2 align-middle">
                      <Badge tone="muted">deferred</Badge>
                    </span>
                  )}
                </td>
                <td className="px-3 py-2 font-mono text-[12px] muted">{m.tool}</td>
                <td className="px-3 py-2">{m.approach}</td>
                <td className="px-3 py-2 muted">{m.solution_type}</td>
                <td className="px-3 py-2">
                  <span className="flex flex-wrap gap-1">
                    {m.citations.slice(0, 3).map((c) => (
                      <Link key={c.id} href={`/docs/standards#${c.id}`}>
                        <Badge tone={c.standard === "IVS" ? "primary" : "gold"}>{c.id}</Badge>
                      </Link>
                    ))}
                    {m.citations.length > 3 && <Badge tone="muted">+{m.citations.length - 3}</Badge>}
                    {m.citations.length === 0 && <span className="text-[12px] muted">—</span>}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
