import Link from "next/link";
import { counts } from "@/lib/catalog";

const COLUMNS = [
  {
    title: "Documentation",
    links: [
      { href: "/docs/getting-started", label: "Getting started" },
      { href: "/docs/mcp", label: "MCP server" },
      { href: "/docs/api", label: "REST API" },
      { href: "/docs/hosting", label: "Hosting" },
    ],
  },
  {
    title: "Reference",
    links: [
      { href: "/docs/methods", label: "Methods catalogue" },
      { href: "/docs/standards", label: "Standards" },
      { href: "/docs/playground", label: "Playground" },
      { href: "/docs/examples", label: "Examples" },
    ],
  },
  {
    title: "Project",
    links: [
      { href: "/docs/status", label: "Status & roadmap" },
      { href: "/docs/slo", label: "Observability" },
      { href: "/docs/changelog", label: "Changelog" },
      { href: "https://github.com/simonmak-ascent/fair-value", label: "GitHub" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="mt-20 border-t border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-950">
      <div className="container-site grid gap-10 py-12 md:grid-cols-[1.4fr_1fr_1fr_1fr]">
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-2.5">
            <span className="grid h-7 w-7 place-items-center rounded-sm bg-primary-600 font-heading text-sm font-bold text-white">
              fv
            </span>
            <span className="font-heading text-[15px] font-semibold">fair-value</span>
          </div>
          <p className="max-w-xs text-[13px] leading-relaxed muted">
            {counts.methods} valuation methods across {counts.tools} MCP tools, {counts.cited} cited to
            IVS 2025 / IFRS-IAS, exposed over MCP and REST.
          </p>
          <p className="text-[12px] muted">
            Information only — not investment advice.
          </p>
        </div>

        {COLUMNS.map((col) => (
          <div key={col.title} className="flex flex-col gap-3">
            <h3 className="font-heading text-[12px] font-semibold uppercase tracking-wider text-neutral-500 dark:text-neutral-400">
              {col.title}
            </h3>
            <ul className="flex flex-col gap-2">
              {col.links.map((link) => (
                <li key={link.href}>
                  {link.href.startsWith("http") ? (
                    <a
                      href={link.href}
                      className="text-[13px] text-neutral-600 transition-colors hover:text-primary-600 dark:text-neutral-300 dark:hover:text-primary-300"
                    >
                      {link.label}
                    </a>
                  ) : (
                    <Link
                      href={link.href}
                      className="text-[13px] text-neutral-600 transition-colors hover:text-primary-600 dark:text-neutral-300 dark:hover:text-primary-300"
                    >
                      {link.label}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="border-t border-neutral-200 dark:border-neutral-800">
        <div className="container-site flex flex-wrap items-center justify-between gap-2 py-4 text-[12px] muted">
          <span>© {new Date().getFullYear()} Ascent Partners Group Ltd · MIT licensed</span>
          <span>fair-value.ascent-partners.com</span>
        </div>
      </div>
    </footer>
  );
}
