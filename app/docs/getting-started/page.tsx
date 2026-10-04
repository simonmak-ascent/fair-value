import Link from "next/link";
import { DocsHeader, Prose } from "@/components/docs/DocsHeader";
import { CodeBlock } from "@/components/ui/CodeBlock";

export const metadata = { title: "Getting started" };

const UVX = `# run locally over stdio — no install
uvx --from "fair-value[mcp]" fair-value-mcp`;

const PY = `# library only, or + MCP server
pip install fair-value
pip install "fair-value[mcp]"
fair-value-mcp            # stdio
fair-value-mcp --http     # Streamable HTTP`;

const FIRST = `curl -s -X POST https://fair-value.ascent-partners.com/v1/calculate/calculate_dcf \\
  -H 'content-type: application/json' \\
  -d '{"method":"dcf","cash_flows":[100,110,121],"discount_rate":0.10}'`;

const HELP = `# the transparency record for a tool (also: help=true)
curl -s -X POST https://fair-value.ascent-partners.com/v1/calculate/calculate_dcf \\
  -H 'content-type: application/json' \\
  -d '{"method":"-help"}'`;

export default function GettingStarted() {
  return (
    <div className="flex flex-col gap-8">
      <DocsHeader
        eyebrow="Get started"
        title="Getting started"
        description="Call 138 valuation methods in under five minutes — over MCP, REST, or Python."
      />

      <Prose>
        <p>
          The fastest path needs no install: point an MCP client at the hosted endpoint, or call the
          REST API. Both reach the same engine and return the same result envelope.
        </p>
        <h2>1 · Connect an MCP client</h2>
        <p>
          Add the hosted Streamable HTTP endpoint to your MCP config — see{" "}
          <Link href="/docs/mcp">the MCP server page</Link> for client snippets.
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
        <h2>2 · Or run it yourself</h2>
      </Prose>
      <CodeBlock label="uvx" code={UVX} />
      <CodeBlock label="pip" code={PY} />

      <Prose>
        <h2>3 · Or call the REST API</h2>
      </Prose>
      <CodeBlock label="curl" code={FIRST} />

      <Prose>
        <h2>4 · Read a tool before you call it</h2>
        <p>
          Every tool answers a generated transparency record (inputs, formula reference, governing
          clause text, risks) via <code>-help</code> or <code>help=true</code>, or in the{" "}
          <Link href="/docs/methods">methods catalogue</Link>.
        </p>
      </Prose>
      <CodeBlock label="curl" code={HELP} />
    </div>
  );
}
