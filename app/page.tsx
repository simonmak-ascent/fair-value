import Link from "next/link";
import { CodeBlock } from "@/components/ui/CodeBlock";
import { Stat } from "@/components/ui/Stat";
import { Badge } from "@/components/ui/Badge";
import { LiveHealth } from "@/components/LiveHealth";
import { counts, standards, tools } from "@/lib/catalog";
import { toolLabel } from "@/lib/utils";

const CAPABILITIES = [
  {
    title: "Standards-aligned",
    body: "Every method maps to verbatim IVS / IFRS / IAS clauses via a data taxonomy; a conformance gate fails CI if a published method loses its citation.",
  },
  {
    title: "Deterministic-first",
    body: "Closed-form and numeric methods by default. The few stochastic methods require a seed and return the distribution — centre, dispersion, percentiles.",
  },
  {
    title: "MCP · REST · Python",
    body: "One registry, three surfaces: a FastMCP server, a versioned /v1 REST API, and the valuation_engine Python facade.",
  },
  {
    title: "Transparent by construction",
    body: "Every tool answers -help with a generated record: inputs, formula reference, governing clause text, risks and limits.",
  },
  {
    title: "Full asset coverage",
    body: "Corporate, startup and intangible valuation; fixed income curves; options and structured products; IFRS 9 credit; IFRS 17 / IAS 19 actuarial.",
  },
  {
    title: "Reproducible",
    body: "Same inputs produce the same envelope. Citations and statistics travel with the value so a reviewer can audit the result.",
  },
];

const MCP_CONFIG = `{
  "mcpServers": {
    "fair-value": {
      "url": "https://fair-value.ascent-partners.com/mcp"
    }
  }
}`;

const CURL = `curl -s -X POST https://fair-value.ascent-partners.com/v1/calculate/calculate_dcf \\
  -H 'content-type: application/json' \\
  -d '{"method":"dcf","cash_flows":[100,110,121],"discount_rate":0.10}'`;

const PY = `from valuation_engine import run_valuation

result = run_valuation("9988.HK", "dcf")   # shared envelope
print(result["value"], result["statistics"]["distribution"])`;

export default function HomePage() {
  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="border-b border-neutral-200 dark:border-neutral-800">
        <div className="container-site grid gap-10 py-16 lg:grid-cols-[1.15fr_0.85fr] lg:py-24">
          <div className="flex flex-col gap-6">
            <div className="flex flex-wrap items-center gap-3">
              <Badge tone="primary">IVS 2025</Badge>
              <Badge tone="primary">IFRS / IAS</Badge>
              <LiveHealth />
            </div>
            <h1 className="max-w-2xl font-heading text-4xl font-semibold leading-[1.1] tracking-tight lg:text-[52px]">
              Valuation, as a <span className="text-primary-600 dark:text-primary-300">governed API</span>.
            </h1>
            <p className="max-w-xl text-[15px] leading-relaxed muted">
              {counts.methods} valuation methods across {counts.tools} MCP tools — DCF and market
              approaches, cost of capital, options, fixed income, credit risk and actuarial PV — each
              returning a deterministic-first envelope with statistics and verbatim standard
              citations.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link
                href="/docs/getting-started"
                className="rounded-md bg-primary-600 px-4 py-2 text-[13px] font-semibold text-white transition-colors hover:bg-primary-700"
              >
                Read the docs
              </Link>
              <Link
                href="/docs/playground"
                className="rounded-md border border-neutral-300 px-4 py-2 text-[13px] font-semibold transition-colors hover:border-primary-500 hover:text-primary-600 dark:border-neutral-700 dark:hover:border-primary-400 dark:hover:text-primary-300"
              >
                Open the playground
              </Link>
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-x-8 gap-y-4 sm:grid-cols-4">
              <Stat value={counts.methods} label="methods" accent />
              <Stat value={counts.tools} label="MCP tools" />
              <Stat value={counts.cited} label="cited" />
              <Stat value={counts.clauses} label="clauses" />
            </dl>
          </div>

          <div className="flex flex-col gap-4">
            <div className="card p-4">
              <h2 className="mb-3 font-heading text-[13px] font-semibold uppercase tracking-wide text-neutral-500 dark:text-neutral-400">
                Endpoints
              </h2>
              <ul className="flex flex-col gap-2 font-mono text-[12.5px]">
                <li className="flex items-center justify-between gap-4">
                  <span className="text-primary-700 dark:text-primary-300">/mcp</span>
                  <span className="muted">Streamable HTTP</span>
                </li>
                <li className="flex items-center justify-between gap-4">
                  <span className="text-primary-700 dark:text-primary-300">/v1/calculate/&#123;tool&#125;</span>
                  <span className="muted">POST</span>
                </li>
                <li className="flex items-center justify-between gap-4">
                  <span className="text-primary-700 dark:text-primary-300">/v1/methods</span>
                  <span className="muted">GET</span>
                </li>
                <li className="flex items-center justify-between gap-4">
                  <span className="text-primary-700 dark:text-primary-300">/v1/standards</span>
                  <span className="muted">GET</span>
                </li>
              </ul>
            </div>
            <CodeBlock label="mcp.json" code={MCP_CONFIG} />
          </div>
        </div>
      </section>

      {/* Capabilities */}
      <section className="border-b border-neutral-200 dark:border-neutral-800">
        <div className="container-site py-16">
          <h2 className="font-heading text-2xl font-semibold tracking-tight">What it guarantees</h2>
          <p className="mt-2 max-w-2xl text-[14px] muted">
            Built for auditable, reproducible valuation — not a black box.
          </p>
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {CAPABILITIES.map((cap) => (
              <div key={cap.title} className="card flex flex-col gap-2 p-5">
                <h3 className="font-heading text-[15px] font-semibold text-primary-700 dark:text-primary-300">
                  {cap.title}
                </h3>
                <p className="text-[13px] leading-relaxed muted">{cap.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Quickstart */}
      <section className="border-b border-neutral-200 dark:border-neutral-800">
        <div className="container-site grid gap-6 py-16 lg:grid-cols-3">
          <div className="lg:col-span-1">
            <h2 className="font-heading text-2xl font-semibold tracking-tight">Three ways in</h2>
            <p className="mt-2 text-[14px] muted">
              Point an MCP client at the hosted endpoint, call the REST API, or use the Python
              library. See{" "}
              <Link href="/docs/getting-started" className="text-primary-600 underline dark:text-primary-300">
                getting started
              </Link>
              .
            </p>
          </div>
          <div className="grid gap-4 lg:col-span-2">
            <CodeBlock label="REST · curl" code={CURL} />
            <CodeBlock label="Python" code={PY} />
          </div>
        </div>
      </section>

      {/* Tool coverage */}
      <section className="border-b border-neutral-200 dark:border-neutral-800">
        <div className="container-site py-16">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <h2 className="font-heading text-2xl font-semibold tracking-tight">14 tools</h2>
              <p className="mt-2 text-[14px] muted">
                {counts.implemented} of {counts.methods} methods implemented · {counts.deferred} deferred
                · {counts.cited} cited · {counts.orphan_clauses} orphan clauses.
              </p>
            </div>
            <Link
              href="/docs/methods"
              className="text-[13px] font-semibold text-primary-600 hover:underline dark:text-primary-300"
            >
              Browse all methods →
            </Link>
          </div>
          <div className="mt-8 grid gap-px overflow-hidden rounded-md border border-neutral-200 bg-neutral-200 sm:grid-cols-2 lg:grid-cols-4 dark:border-neutral-800 dark:bg-neutral-800">
            {tools.map((tool) => (
              <Link
                key={tool.id}
                href="/docs/methods"
                className="flex flex-col gap-1 bg-white p-4 transition-colors hover:bg-neutral-50 dark:bg-neutral-950 dark:hover:bg-neutral-900"
              >
                <span className="font-heading text-[14px] font-semibold">{toolLabel(tool.id)}</span>
                <span className="text-[12px] muted">{tool.methods.length} methods</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Standards strip */}
      <section>
        <div className="container-site py-16">
          <h2 className="font-heading text-2xl font-semibold tracking-tight">Aligned to the standards</h2>
          <p className="mt-2 max-w-2xl text-[14px] muted">
            Verbatim clause text is committed in-repo with provenance; the taxonomy maps each method to
            its IVS and IFRS/IAS clauses.
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            {standards.map((s) => (
              <Link key={s.id} href="/docs/standards" className="card px-3 py-1.5 text-[12.5px] hover:border-primary-400">
                <span className="font-medium">{s.title}</span>
                <span className="ml-2 muted">{s.edition}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
