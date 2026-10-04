"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/docs", label: "Docs" },
  { href: "/docs/methods", label: "Methods" },
  { href: "/docs/standards", label: "Standards" },
  { href: "/docs/api", label: "API" },
  { href: "/docs/playground", label: "Playground" },
];

export function Header() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-neutral-200 bg-white/85 backdrop-blur dark:border-neutral-800 dark:bg-neutral-950/85">
      <div className="container-site flex h-14 items-center gap-6">
        <Link href="/" className="flex items-center gap-2.5" aria-label="fair-value home">
          <span className="grid h-7 w-7 place-items-center rounded-sm bg-primary-600 font-heading text-sm font-bold text-white">
            fv
          </span>
          <span className="font-heading text-[15px] font-semibold tracking-tight">fair-value</span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex" aria-label="Primary">
          {NAV.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "rounded-md px-3 py-1.5 text-[13px] font-medium transition-colors",
                  active
                    ? "bg-neutral-100 text-primary-700 dark:bg-neutral-800 dark:text-primary-300"
                    : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 dark:text-neutral-300 dark:hover:bg-neutral-800 dark:hover:text-white",
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <a
            href="https://github.com/simonmak-ascent/fair-value"
            className="hidden rounded-md px-2 py-1.5 text-[13px] font-medium text-neutral-600 transition-colors hover:text-neutral-900 sm:block dark:text-neutral-300 dark:hover:text-white"
          >
            GitHub
          </a>
          <ThemeToggle />
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle navigation"
            aria-expanded={open}
            className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-neutral-300 text-neutral-600 md:hidden dark:border-neutral-700 dark:text-neutral-300"
          >
            <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
              {open ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M3 6h18M3 12h18M3 18h18" />}
            </svg>
          </button>
        </div>
      </div>

      {open && (
        <nav className="border-t border-neutral-200 md:hidden dark:border-neutral-800" aria-label="Mobile">
          <div className="container-site flex flex-col py-2">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setOpen(false)}
                className="rounded-md px-2 py-2 text-sm text-neutral-700 hover:bg-neutral-100 dark:text-neutral-200 dark:hover:bg-neutral-800"
              >
                {item.label}
              </Link>
            ))}
          </div>
        </nav>
      )}
    </header>
  );
}
