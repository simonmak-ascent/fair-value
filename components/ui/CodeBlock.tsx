"use client";

import { useState } from "react";

export function CodeBlock({
  code,
  label,
  className = "",
}: {
  code: string;
  label?: string;
  className?: string;
}) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* ignore */
    }
  }

  return (
    <div className={`card overflow-hidden ${className}`}>
      <div className="flex items-center justify-between border-b border-neutral-200 bg-neutral-50 px-3 py-1.5 dark:border-neutral-800 dark:bg-neutral-900">
        <span className="font-mono text-[11px] uppercase tracking-wide text-neutral-500 dark:text-neutral-400">
          {label ?? "shell"}
        </span>
        <button
          type="button"
          onClick={copy}
          className="rounded px-2 py-0.5 text-[11px] font-medium text-neutral-500 transition-colors hover:text-primary-600 dark:text-neutral-400 dark:hover:text-primary-300"
        >
          {copied ? "copied" : "copy"}
        </button>
      </div>
      <pre className="scroll-thin overflow-x-auto bg-white p-3 text-[12.5px] leading-relaxed dark:bg-neutral-950">
        <code className="font-mono text-neutral-800 dark:text-neutral-200">{code}</code>
      </pre>
    </div>
  );
}
