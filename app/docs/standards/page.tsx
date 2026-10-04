import { DocsHeader, Prose } from "@/components/docs/DocsHeader";
import { StandardsBrowser } from "@/components/docs/StandardsBrowser";
import { counts, standards } from "@/lib/catalog";

export const metadata = { title: "Standards" };

export default function StandardsPage() {
  return (
    <div className="flex flex-col gap-6">
      <DocsHeader
        eyebrow="Reference"
        title="Standards"
        description={`${counts.clauses} verbatim clauses across ${standards.length} standards. ${counts.cited} of ${counts.methods} methods cite at least one clause; ${counts.orphan_clauses} clauses are orphaned.`}
      />
      <Prose>
        <p>
          The alignment is data, not code: <code>standards/taxonomy.json</code> maps each method to
          its IVS and IFRS/IAS clauses, and <code>standards/source/*.md</code> holds the verbatim
          clause text with provenance. § numbering is cross-checked against the HKICPA HKFRS/HKAS
          adoptions.
        </p>
      </Prose>
      <StandardsBrowser />
    </div>
  );
}
