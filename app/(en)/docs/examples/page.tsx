import { DocsHeader, Prose } from "@/components/docs/DocsHeader";

export const metadata = { title: "Examples" };

const EXAMPLES: [string, string, string][] = [
  ["HKD convertible bond, 3y with a 2y issuer call at par", "calculate_convertible_bond · lattice_tsf", "~112.4"],
  ["HKEX inline range warrant (90–110, pays 1)", "calculate_structured_product · inline_warrant", "~4231.7"],
  ["Loss-making listing, margin-ramp DCF", "calculate_loss_making_company · margin_ramp_dcf", "~24.0 / share"],
];

export default function ExamplesPage() {
  return (
    <div className="flex flex-col gap-6">
      <DocsHeader
        eyebrow="Reference"
        title="Examples"
        description="Worked Hong Kong market examples, run offline against the engine. Monte-Carlo methods are seeded, so output is deterministic."
      />
      <div className="overflow-hidden rounded-md border border-neutral-200 dark:border-neutral-800">
        <table className="w-full border-collapse text-[13px]">
          <thead>
            <tr className="border-b border-neutral-200 bg-neutral-50 text-left dark:border-neutral-800 dark:bg-neutral-900">
              <th className="px-3 py-2 font-medium">Scenario</th>
              <th className="px-3 py-2 font-medium">Method</th>
              <th className="px-3 py-2 font-medium">Value</th>
            </tr>
          </thead>
          <tbody>
            {EXAMPLES.map(([scenario, method, value]) => (
              <tr key={scenario} className="border-b border-neutral-100 last:border-0 dark:border-neutral-900">
                <td className="px-3 py-2">{scenario}</td>
                <td className="px-3 py-2 font-mono text-[12px] muted">{method}</td>
                <td className="px-3 py-2 tabular-nums">{value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Prose>
        <p>The examples live in <code>examples/hk_examples.py</code> and are exercised by the test suite, so they stay in step with the registry.</p>
      </Prose>
    </div>
  );
}
