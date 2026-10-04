import { DocsHeader } from "@/components/docs/DocsHeader";
import { MethodsExplorer } from "@/components/docs/MethodsExplorer";
import { counts } from "@/lib/catalog";

export const metadata = { title: "Methods" };

export default function MethodsPage() {
  return (
    <div className="flex flex-col gap-6">
      <DocsHeader
        eyebrow="Reference"
        title="Methods catalogue"
        description={`${counts.methods} methods across ${counts.tools} tools. ${counts.cited} carry IVS/IFRS citations; each entry links to its inputs, formula reference and governing clauses.`}
      />
      <MethodsExplorer />
    </div>
  );
}
