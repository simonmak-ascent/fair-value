import Link from "next/link";
import { counts } from "@/lib/catalog";

const CARDS = [
  {
    href: "/docs/getting-started",
    title: "Getting started",
    body: "Install, run over stdio, or point a client at the hosted endpoint.",
  },
  {
    href: "/docs/mcp",
    title: "MCP server",
    body: "Transports, the 14 tools, `-help`, and the valuation:// resources.",
  },
  {
    href: "/docs/api",
    title: "REST API",
    body: "The versioned /v1 surface, the result envelope, and OpenAPI.",
  },
  {
    href: "/docs/playground",
    title: "Playground",
    body: "Call any of the 135 methods with a generated input form.",
  },
  {
    href: "/docs/methods",
    title: "Methods catalogue",
    body: `${counts.methods} methods with inputs, formula references and clauses.`,
  },
  {
    href: "/docs/standards",
    title: "Standards",
    body: `${counts.clauses} verbatim clauses across IVS 2025 and IFRS/IAS.`,
  },
];

export default function DocsHub() {
  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-3">
        <h1 className="font-heading text-3xl font-semibold tracking-tight">Documentation</h1>
        <p className="text-[15px] leading-relaxed muted">
          Everything you need to call the {counts.methods} valuation methods over MCP, REST, or Python
          — with the standards citations that travel with every result.
        </p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2">
        {CARDS.map((card) => (
          <Link key={card.href} href={card.href} className="card flex flex-col gap-2 p-5 transition-colors hover:border-primary-400">
            <span className="font-heading text-[15px] font-semibold text-primary-700 dark:text-primary-300">
              {card.title}
            </span>
            <span className="text-[13px] leading-relaxed muted">{card.body}</span>
          </Link>
        ))}
      </div>

      <section className="card flex flex-col gap-3 p-5">
        <h2 className="font-heading text-[15px] font-semibold">At a glance</h2>
        <ul className="grid grid-cols-2 gap-y-2 text-[13px] sm:grid-cols-3">
          <li><span className="font-semibold">{counts.tools}</span> <span className="muted">tools</span></li>
          <li><span className="font-semibold">{counts.methods}</span> <span className="muted">methods</span></li>
          <li><span className="font-semibold">{counts.implemented}</span> <span className="muted">implemented</span></li>
          <li><span className="font-semibold">{counts.cited}</span> <span className="muted">cited</span></li>
          <li><span className="font-semibold">{counts.clauses}</span> <span className="muted">clauses</span></li>
          <li><span className="font-semibold">{counts.orphan_clauses}</span> <span className="muted">orphans</span></li>
        </ul>
      </section>
    </div>
  );
}
