"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const SECTIONS: { title: string; links: { href: string; label: string }[] }[] = [
  {
    title: "Get started",
    links: [
      { href: "/docs", label: "Overview" },
      { href: "/docs/getting-started", label: "Getting started" },
    ],
  },
  {
    title: "Interfaces",
    links: [
      { href: "/docs/mcp", label: "MCP server" },
      { href: "/docs/api", label: "REST API" },
      { href: "/docs/playground", label: "Playground" },
    ],
  },
  {
    title: "Reference",
    links: [
      { href: "/docs/methods", label: "Methods catalogue" },
      { href: "/docs/standards", label: "Standards" },
      { href: "/docs/examples", label: "Examples" },
    ],
  },
  {
    title: "Operate",
    links: [
      { href: "/docs/hosting", label: "Hosting" },
      { href: "/docs/status", label: "Status & roadmap" },
      { href: "/docs/slo", label: "Observability" },
      { href: "/docs/changelog", label: "Changelog" },
    ],
  },
];

export function DocsSidebar() {
  const pathname = usePathname();

  return (
    <nav aria-label="Docs" className="flex flex-col gap-6 text-[13px]">
      {SECTIONS.map((section) => (
        <div key={section.title} className="flex flex-col gap-2">
          <span className="font-heading text-[11px] font-semibold uppercase tracking-wider text-neutral-500 dark:text-neutral-500">
            {section.title}
          </span>
          <ul className="flex flex-col gap-0.5">
            {section.links.map((link) => {
              const active =
                pathname === link.href ||
                (link.href !== "/docs" && pathname.startsWith(`${link.href}/`));
              return (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className={cn(
                      "block rounded px-2 py-1 transition-colors",
                      active
                        ? "bg-primary-50 font-medium text-primary-700 dark:bg-primary-950 dark:text-primary-300"
                        : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 dark:text-neutral-400 dark:hover:bg-neutral-900 dark:hover:text-white",
                    )}
                  >
                    {link.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </nav>
  );
}
