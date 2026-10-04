import { DocsHeader, Prose } from "@/components/docs/DocsHeader";
import { CodeBlock } from "@/components/ui/CodeBlock";

export const metadata = { title: "Hosting" };

export default function HostingPage() {
  return (
    <div className="flex flex-col gap-6">
      <DocsHeader
        eyebrow="Operate"
        title="Hosting"
        description="The server runs over stdio by default and Streamable HTTP with --http. The public frontage and API deploy on Vercel."
      />
      <Prose>
        <h2>Hosted (zero install)</h2>
        <ul>
          <li><code>https://fair-value.ascent-partners.com/mcp</code> — MCP Streamable HTTP</li>
          <li><code>https://fair-value.ascent-partners.com/v1/…</code> — REST API</li>
        </ul>
        <p>
          Deployed from <code>api/index.py</code> (the MCP + REST ASGI app) with the Next.js frontage
          in the same Vercel project. The MCP endpoint moved from the domain root to <code>/mcp</code>.
        </p>

        <h2>Docker</h2>
      </Prose>
      <CodeBlock
        label="shell"
        code={`docker build -t fair-value-mcp .
docker run --rm -p 8000:8000 fair-value-mcp
# MCP endpoint: http://localhost:8000/mcp

# docker compose
SENTRY_DSN="" docker compose up --build`}
      />

      <Prose>
        <h2>Self-host (uvicorn)</h2>
      </Prose>
      <CodeBlock label="shell" code={`uvicorn mcp_server.asgi:app --host 0.0.0.0 --port 8000`} />

      <Prose>
        <h2>Configuration</h2>
        <ul>
          <li><code>SENTRY_DSN</code> — enables error/tracing telemetry when set (off by default).</li>
          <li><code>SENTRY_ENVIRONMENT</code>, <code>SENTRY_RELEASE</code> — telemetry tags.</li>
        </ul>
      </Prose>
    </div>
  );
}
