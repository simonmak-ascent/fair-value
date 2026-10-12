import Link from "next/link";
import { notFound } from "next/navigation";
import { DocsHeader, Prose } from "@/components/docs/DocsHeader";
import { CodeBlock } from "@/components/ui/CodeBlock";
import { Badge } from "@/components/ui/Badge";
import { getMethod, methods } from "@/lib/catalog";

export function generateStaticParams() {
  return methods.map((m) => ({ method: m.method }));
}

export function generateMetadata({ params }: { params: Promise<{ method: string }> }) {
  return params.then(({ method }) => {
    const m = getMethod(method);
    return { title: m ? `${m.method} — ${m.tool}` : "Method" };
  });
}

export default async function MethodPage({ params }: { params: Promise<{ method: string }> }) {
  const { method } = await params;
  const m = getMethod(method);
  if (!m) notFound();

  const restCall = `curl -s -X POST https://fair-value.ascent-partners.com/v1/calculate/${m.tool} \\
  -H 'content-type: application/json' \\
  -d '${JSON.stringify({ method: m.method }, null, 0)}'`;

  const mcpCall = `// MCP tools/call
{ "name": "${m.tool}",
  "arguments": { "method": "${m.method}" } }`;

  return (
    <div className="flex flex-col gap-8">
      <nav className="text-[12.5px] muted">
        <Link href="/docs/methods" className="hover:text-primary-600 dark:hover:text-primary-300">
          Methods
        </Link>{" "}
        / <span className="font-mono">{m.method}</span>
      </nav>

      <DocsHeader eyebrow={m.tool} title={m.method} description={m.summary} />

      <div className="flex flex-wrap gap-2">
        <Badge tone="primary">{m.approach}</Badge>
        <Badge>{m.solution_type}</Badge>
        {m.standards.map((s) => (
          <Badge key={s}>{s}</Badge>
        ))}
        {m.implemented ? (
          <Badge tone="primary">implemented</Badge>
        ) : (
          <Badge tone="muted">deferred</Badge>
        )}
      </div>

      <Prose>
        <p>
          <strong>Formula reference:</strong> {m.formula_ref || "—"}
        </p>
      </Prose>

      <section className="flex flex-col gap-3">
        <h2 className="font-heading text-lg font-semibold">Inputs</h2>
        {m.inputs.length === 0 ? (
          <p className="text-[13px] muted">No inputs.</p>
        ) : (
          <div className="overflow-x-auto rounded-md border border-neutral-200 dark:border-neutral-800">
            <table className="w-full min-w-[600px] border-collapse text-[13px]">
              <thead>
                <tr className="border-b border-neutral-200 bg-neutral-50 text-left dark:border-neutral-800 dark:bg-neutral-900">
                  <th className="px-3 py-2 font-medium">Name</th>
                  <th className="px-3 py-2 font-medium">Type</th>
                  <th className="px-3 py-2 font-medium">Req</th>
                  <th className="px-3 py-2 font-medium">Description</th>
                </tr>
              </thead>
              <tbody>
                {m.inputs.map((input) => (
                  <tr key={input.name} className="border-b border-neutral-100 last:border-0 dark:border-neutral-900">
                    <td className="px-3 py-2 font-mono text-[12.5px]">{input.name}</td>
                    <td className="px-3 py-2 muted">{input.type}</td>
                    <td className="px-3 py-2">{m.required.includes(input.name) ? "✓" : "—"}</td>
                    <td className="px-3 py-2 muted">{input.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {m.citations.length > 0 && (
        <section className="flex flex-col gap-3">
          <h2 className="font-heading text-lg font-semibold">Standards</h2>
          <div className="flex flex-col gap-2">
            {m.citations.map((c) => (
              <Link
                key={c.id}
                href={`/docs/standards#${c.id}`}
                className="card flex flex-col gap-1 p-3 transition-colors hover:border-primary-400"
              >
                <span className="flex items-center gap-2">
                  <Badge tone={c.standard === "IVS" ? "primary" : "gold"}>{c.id}</Badge>
                  <span className="text-[13px] font-medium">{c.label}</span>
                </span>
                <span className="text-[12.5px] muted">{c.summary}</span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {m.risks.length > 0 && (
        <Prose>
          <h2>Risks &amp; limits</h2>
          <ul>
            {m.risks.map((risk) => (
              <li key={risk}>{risk}</li>
            ))}
          </ul>
        </Prose>
      )}

      <section className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <h2 className="font-heading text-lg font-semibold">Call it</h2>
          <Link
            href={`/docs/playground?method=${m.method}`}
            className="text-[13px] font-semibold text-primary-600 hover:underline dark:text-primary-300"
          >
            Try in playground →
          </Link>
        </div>
        <CodeBlock label="REST" code={restCall} />
        <CodeBlock label="MCP" code={mcpCall} />
      </section>
    </div>
  );
}
