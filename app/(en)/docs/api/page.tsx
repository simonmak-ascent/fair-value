import Link from "next/link";
import { DocsHeader, Prose } from "@/components/docs/DocsHeader";
import { CodeBlock } from "@/components/ui/CodeBlock";

export const metadata = { title: "REST API" };

const ENDPOINTS: [string, string, string][] = [
  ["GET", "/v1/health", "Service + surface version, tool count"],
  ["GET", "/v1/tools", "Tools with titles, descriptions and methods"],
  ["GET", "/v1/methods", "Full method catalog (parameters, formula refs, standards)"],
  ["GET", "/v1/standards", "Standards, clauses, and the methods citing each"],
  ["GET", "/v1/openapi.json", "OpenAPI 3.0 document for this API"],
  ["GET", "/v1/docs", "Swagger UI for the API"],
  ["GET", "/v1/help/{tool}", "Generated transparency record for a tool"],
  ["POST", "/v1/calculate/{tool}", "Run a method: {\"method\": \"...\", ...inputs}"],
];

const ENVELOPE = `{
  "status": "ok",
  "method": "calculate_dcf.dcf",
  "value": 183.4,
  "statistics": {
    "solution_type": "closed_form",
    "distribution": "deterministic",
    "centre": 183.4,
    "sigma": 0.0,
    "percentiles": { "p05": 183.4, "p50": 183.4, "p95": 183.4 },
    "samples": null,
    "seed": null
  },
  "solution_type": "closed_form",
  "citations": { "ivs": ["IVS.103.A20"], "ifrs": ["IFRS.13.61", "IFRS.13.62"] },
  "disclaimer": "..."
}`;

export default function ApiPage() {
  return (
    <div className="flex flex-col gap-8">
      <DocsHeader
        eyebrow="Interface"
        title="REST API"
        description="The same engine as the MCP tools, exposed as a versioned REST surface at /v1."
      />

      <Prose>
        <p>
          Every call returns the shared envelope — centre value, <code>statistics</code>,{" "}
          <code>solution_type</code> and <code>citations</code>. No method logic is duplicated. The
          machine-readable contract is served at{" "}
          <a href="/v1/openapi.json">/v1/openapi.json</a> (Swagger UI at{" "}
          <a href="/v1/docs">/v1/docs</a>).
        </p>
      </Prose>

      <section className="flex flex-col gap-3">
        <h2 className="font-heading text-lg font-semibold">Endpoints</h2>
        <div className="overflow-hidden rounded-md border border-neutral-200 dark:border-neutral-800">
          <table className="w-full border-collapse text-[13px]">
            <thead>
              <tr className="border-b border-neutral-200 bg-neutral-50 text-left dark:border-neutral-800 dark:bg-neutral-900">
                <th className="px-3 py-2 font-medium">Method</th>
                <th className="px-3 py-2 font-medium">Path</th>
                <th className="px-3 py-2 font-medium">Description</th>
              </tr>
            </thead>
            <tbody>
              {ENDPOINTS.map(([method, path, desc]) => (
                <tr key={path} className="border-b border-neutral-100 last:border-0 dark:border-neutral-900">
                  <td className="px-3 py-2">
                    <span className="font-mono text-[12px] text-primary-600 dark:text-primary-300">{method}</span>
                  </td>
                  <td className="px-3 py-2 font-mono text-[12.5px]">{path}</td>
                  <td className="px-3 py-2 muted">{desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <Prose>
        <h2>Example</h2>
      </Prose>
      <CodeBlock
        label="curl"
        code={`curl -s -X POST https://fair-value.ascent-partners.com/v1/calculate/calculate_dcf \\
  -H 'content-type: application/json' \\
  -d '{"method":"dcf","cash_flows":[100,110],"discount_rate":0.1}'`}
      />

      <Prose>
        <h2>Result envelope</h2>
      </Prose>
      <CodeBlock label="json" code={ENVELOPE} />

      <Prose>
        <p>
          Errors return <code>400</code> (invalid method/body) or <code>404</code> (unknown tool) with a{" "}
          <code>{'{"status":"error","error":…}'}</code> body. Try any method in the{" "}
          <Link href="/docs/playground">playground</Link>.
        </p>
      </Prose>
    </div>
  );
}
