"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { clauses, standards } from "@/lib/catalog";
import { cn } from "@/lib/utils";

export function StandardsBrowser() {
  const [q, setQ] = useState("");
  const [standard, setStandard] = useState("");

  const grouped = useMemo(() => {
    const needle = q.trim().toLowerCase();
    const filtered = clauses.filter((c) => {
      if (standard && c.standard !== standard) return false;
      if (!needle) return true;
      return (
        c.id.toLowerCase().includes(needle) ||
        c.label.toLowerCase().includes(needle) ||
        c.summary.toLowerCase().includes(needle) ||
        c.text.toLowerCase().includes(needle)
      );
    });
    const map = new Map<string, typeof filtered>();
    for (const c of filtered) {
      const arr = map.get(c.standard) ?? [];
      arr.push(c);
      map.set(c.standard, arr);
    }
    return map;
  }, [q, standard]);

  const select =
    "rounded-md border border-neutral-300 bg-white px-2.5 py-1.5 text-[12.5px] dark:border-neutral-700 dark:bg-neutral-900";

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-wrap items-center gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search clauses, labels, text…"
          className={cn(select, "w-full sm:w-72")}
          aria-label="Search clauses"
        />
        <select
          value={standard}
          onChange={(e) => setStandard(e.target.value)}
          className={select}
          aria-label="Filter by standard"
        >
          <option value="">All standards</option>
          {standards.map((s) => (
            <option key={s.id} value={s.id}>
              {s.title}
            </option>
          ))}
        </select>
      </div>

      {Array.from(grouped.entries()).map(([std, items]) => (
        <section key={std} className="flex flex-col gap-3">
          <h2 className="font-heading text-[13px] font-semibold uppercase tracking-wider text-neutral-500 dark:text-neutral-400">
            {standards.find((s) => s.id === std)?.title ?? std} · {items.length}
          </h2>
          <div className="flex flex-col gap-3">
            {items.map((c) => (
              <article key={c.id} id={c.id} className="card scroll-mt-20 p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge tone={c.standard === "IVS" ? "primary" : "gold"}>{c.id}</Badge>
                  <span className="font-heading text-[14px] font-semibold">{c.label}</span>
                </div>
                <p className="mt-2 text-[13px] muted">{c.summary}</p>
                <blockquote className="mt-3 border-l-2 border-primary-500/60 pl-3 font-mono text-[12px] leading-relaxed text-neutral-600 dark:text-neutral-300">
                  {c.text}
                </blockquote>
                {c.cited_by.length > 0 && (
                  <div className="mt-3 flex flex-wrap items-center gap-1.5">
                    <span className="text-[11px] uppercase tracking-wide muted">cited by</span>
                    {c.cited_by.map((method) => (
                      <Link
                        key={method}
                        href={`/docs/methods/${method}`}
                        className="rounded border border-neutral-200 px-1.5 py-0.5 font-mono text-[11px] hover:border-primary-400 hover:text-primary-600 dark:border-neutral-800 dark:hover:text-primary-300"
                      >
                        {method}
                      </Link>
                    ))}
                  </div>
                )}
              </article>
            ))}
          </div>
        </section>
      ))}

      {grouped.size === 0 && <p className="text-[13px] muted">No clauses match.</p>}
    </div>
  );
}
