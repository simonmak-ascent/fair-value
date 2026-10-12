"use client";

import { useState } from "react";

export function ConnectTabs({
  clients,
  copyLabel,
  copiedLabel,
  ariaLabel,
}: {
  clients: { key: string; label: string; code: string }[];
  copyLabel: string;
  copiedLabel: string;
  ariaLabel: string;
}) {
  const [active, setActive] = useState(clients[0]?.key ?? "");
  const [copied, setCopied] = useState(false);
  const current = clients.find((c) => c.key === active) ?? clients[0];

  async function copy() {
    if (!current) return;
    try {
      await navigator.clipboard.writeText(current.code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard unavailable */
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div role="tablist" aria-label={ariaLabel} className="flex flex-wrap gap-1 border-b border-neutral-200 pb-2 dark:border-neutral-800">
        {clients.map((c) => (
          <button
            key={c.key}
            role="tab"
            type="button"
            aria-selected={c.key === active}
            onClick={() => setActive(c.key)}
            className={`rounded-md border px-3 py-1.5 text-[12.5px] font-semibold transition-colors ${
              c.key === active
                ? "border-neutral-300 bg-neutral-100 text-neutral-900 dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-100"
                : "border-transparent text-neutral-500 hover:text-primary-600 dark:text-neutral-400 dark:hover:text-primary-300"
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>
      {current && (
        <div className="relative">
          <button
            type="button"
            onClick={copy}
            className="absolute end-2 top-2 rounded-md border border-neutral-300 bg-white px-2.5 py-1 text-[11px] font-semibold text-neutral-500 hover:text-primary-600 dark:border-neutral-700 dark:bg-neutral-950 dark:text-neutral-400 dark:hover:text-primary-300"
          >
            {copied ? copiedLabel : copyLabel}
          </button>
          <pre className="overflow-x-auto rounded-md border border-neutral-200 bg-neutral-100 p-4 font-mono text-[12.5px] text-neutral-900 dark:border-neutral-800 dark:bg-neutral-900 dark:text-neutral-100">
            {current.code}
          </pre>
        </div>
      )}
    </div>
  );
}
