import { DocsHeader, Prose } from "@/components/docs/DocsHeader";
import { CodeBlock } from "@/components/ui/CodeBlock";

export const metadata = { title: "Observability" };

const SLO = `availability        ≥ 0.995   at least   30 days
tool_success_rate   ≥ 0.99    at least   30 days
p95_latency_ms      ≤ 2000    at most     7 days`;

export default function SloPage() {
  return (
    <div className="flex flex-col gap-6">
      <DocsHeader
        eyebrow="Operate"
        title="Observability & SLOs"
        description="Declared SLOs, evaluated by the server, plus optional Sentry telemetry."
      />
      <Prose>
        <h2>Service-level objectives</h2>
      </Prose>
      <CodeBlock label="slo" code={SLO} />
      <Prose>
        <h2>Sentry</h2>
        <p>
          Optional and off by default. When <code>SENTRY_DSN</code> is unset (or <code>sentry-sdk</code>{" "}
          is not installed) the server runs without telemetry and makes no network calls at import time.
        </p>
      </Prose>
      <CodeBlock
        label="shell"
        code={`pip install "fair-value[observability]"
export SENTRY_DSN="https://<key>@o0.ingest.sentry.io/0"
fair-value-mcp`}
      />
    </div>
  );
}
