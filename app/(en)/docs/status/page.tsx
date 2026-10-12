import { DocsHeader, Prose } from "@/components/docs/DocsHeader";
import { Stat } from "@/components/ui/Stat";
import { counts } from "@/lib/catalog";

export const metadata = { title: "Status & roadmap" };

export default function StatusPage() {
  return (
    <div className="flex flex-col gap-6">
      <DocsHeader
        eyebrow="Operate"
        title="Status & roadmap"
        description="The server was redesigned around a single method-spec registry and a standards taxonomy, then expanded to 14 tools / 135 methods."
      />

      <div className="grid grid-cols-2 gap-6 rounded-md border border-neutral-200 p-5 sm:grid-cols-4 dark:border-neutral-800">
        <Stat value={counts.tools} label="tools" accent />
        <Stat value={counts.methods} label="methods" />
        <Stat value={counts.implemented} label="implemented" />
        <Stat value={counts.cited} label="cited" />
      </div>

      <Prose>
        <h2>Current</h2>
        <ul>
          <li>{counts.implemented}/{counts.methods} methods implemented ({counts.deferred} deferred: <code>finite_difference</code>, <code>quantlib</code>).</li>
          <li>{counts.cited}/{counts.methods} cited to IVS 2025 / IFRS-IAS; {counts.orphan_clauses} orphan clauses.</li>
          <li>Deterministic-first: closed-form and numeric by default; stochastic methods are seeded.</li>
          <li>MCP (stdio + Streamable HTTP), REST (<code>/v1</code>), OpenAPI, and a Python facade.</li>
        </ul>

        <h2>Roadmap</h2>
        <ul>
          <li><strong>P1</strong> — <code>finite_difference</code> convertible engine (regime-aware solver; currently dips below the straight-bond floor).</li>
          <li><strong>P1</strong> — enable <code>quantlib</code> conditionally where the optional engine is present (CI installs it).</li>
          <li><strong>P2</strong> — cut the first tagged release (PyPI + MCP Registry).</li>
        </ul>

        <h2>Guarantees enforced in CI</h2>
        <ul>
          <li>Conformance gate: registry + surface + standards coverage (ratchet, no orphan clauses, no uncited method outside the exempt set).</li>
          <li>Generated docs must be in sync; lint, type-check, tests and packaging smoke all green.</li>
        </ul>
      </Prose>
    </div>
  );
}
