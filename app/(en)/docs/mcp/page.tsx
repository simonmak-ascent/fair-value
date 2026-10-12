import Link from "next/link";
import { DocsHeader, Prose } from "@/components/docs/DocsHeader";
import { CodeBlock } from "@/components/ui/CodeBlock";
import { Badge } from "@/components/ui/Badge";
import { tools, counts } from "@/lib/catalog";
import { toolLabel } from "@/lib/utils";

export const metadata = { title: "MCP server" };

export default function McpPage() {
  return (
    <div className="flex flex-col gap-8">
      <DocsHeader
        eyebrow="Interface"
        title="MCP server"
        description={`${counts.tools} native calculate_* tools over Model Context Protocol — stdio or Streamable HTTP.`}
      />

      <Prose>
        <h2>Transports</h2>
        <ul>
          <li>
            <strong>Streamable HTTP</strong> — hosted at{" "}
            <code>https://fair-value.ascent-partners.com/mcp</code>.
          </li>
          <li>
            <strong>stdio</strong> — run <code>fair-value-mcp</code> locally (see{" "}
            <Link href="/docs/getting-started">getting started</Link>).
          </li>
        </ul>
        <p>
          Add the hosted endpoint to any MCP client; the <code>/mcp</code> path is the server root.
        </p>
      </Prose>

      <CodeBlock
        label="mcp.json"
        code={`{
  "mcpServers": {
    "fair-value": {
      "url": "https://fair-value.ascent-partners.com/mcp"
    }
  }
}`}
      />

      <Prose>
        <h2>Resources &amp; help</h2>
        <ul>
          <li>
            <code>valuation://methods</code> — machine-readable catalogue of methods, inputs, formula
            references and governing standards.
          </li>
          <li>
            <code>valuation://standards</code> — the IVS/IFRS taxonomy with clause text and the
            methods citing each.
          </li>
          <li>
            <strong>-help</strong> — call any tool with <code>{'method: "-help"'}</code> (or{" "}
            <code>help=true</code>) for its transparency record.
          </li>
        </ul>
      </Prose>

      <section className="flex flex-col gap-3">
        <h2 className="font-heading text-lg font-semibold">Tools</h2>
        <div className="overflow-hidden rounded-md border border-neutral-200 dark:border-neutral-800">
          <table className="w-full border-collapse text-[13px]">
            <thead>
              <tr className="border-b border-neutral-200 bg-neutral-50 text-left dark:border-neutral-800 dark:bg-neutral-900">
                <th className="px-3 py-2 font-medium">Tool</th>
                <th className="px-3 py-2 font-medium">Methods</th>
                <th className="px-3 py-2 font-medium">Surface</th>
              </tr>
            </thead>
            <tbody>
              {tools.map((tool) => (
                <tr key={tool.id} className="border-b border-neutral-100 last:border-0 dark:border-neutral-900">
                  <td className="px-3 py-2 font-mono text-primary-700 dark:text-primary-300">{tool.id}</td>
                  <td className="px-3 py-2 tabular-nums">{tool.methods.length}</td>
                  <td className="px-3 py-2">
                    <Badge tone={tool.surface === "review" ? "gold" : "neutral"}>{tool.surface}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-[13px] muted">
          {toolLabel("calculate_dcf")} · {toolLabel("calculate_option")} ·{" "}
          {toolLabel("calculate_credit_loss")} and more — see the{" "}
          <Link href="/docs/methods" className="text-primary-600 underline dark:text-primary-300">
            full catalogue
          </Link>
          .
        </p>
      </section>
    </div>
  );
}
