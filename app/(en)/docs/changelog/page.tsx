import { DocsHeader, Prose } from "@/components/docs/DocsHeader";

export const metadata = { title: "Changelog" };

export default function ChangelogPage() {
  return (
    <div className="flex flex-col gap-6">
      <DocsHeader
        eyebrow="Operate"
        title="Changelog"
        description="Standards corpus and taxonomy changes. Machine-readable versions in standards/versions.json."
      />
      <Prose>
        <h2>2025.2 — 2026-10-04</h2>
        <ul>
          <li>
            <strong>IFRS 9</strong> — the measurement wording quoted as §5.5.5 is §5.5.17; added the
            12-month rule as <code>IFRS.9.5.5.5</code> and the measurement basis as{" "}
            <code>IFRS.9.5.5.17</code>.
          </li>
          <li>
            <strong>IFRS 17</strong> — replaced the paraphrased §32 with the verbatim initial-recognition
            text; added the PAA (<code>IFRS.17.53</code>, <code>IFRS.17.55</code>) and VFA (
            <code>IFRS.17.45</code>) clauses.
          </li>
          <li>
            <strong>IAS 19</strong> — the definition quoted as §67 is §68; restored the §67 requirement
            and added <code>IAS.19.68</code>.
          </li>
          <li>§ numbering cross-checked against the HKICPA HKFRS/HKAS adoptions (recorded in provenance).</li>
        </ul>

        <h2>2025.1 — 2026-10-04</h2>
        <ul>
          <li>Initial corpus + dual-standard taxonomy: IVS 103/105/210/220/230/300/400/410/500, IFRS 13/16, IAS 36/37, then IFRS 9/17 and IAS 19.</li>
        </ul>
      </Prose>
    </div>
  );
}
