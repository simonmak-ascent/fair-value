import { Suspense } from "react";
import { DocsHeader, Prose } from "@/components/docs/DocsHeader";
import { Playground } from "@/components/docs/Playground";

export const metadata = { title: "Playground" };

export default function PlaygroundPage() {
  return (
    <div className="flex flex-col gap-6">
      <DocsHeader
        eyebrow="Interface"
        title="Playground"
        description="Call any of the 135 methods with a generated input form. Requests go to the live /v1 API on this host."
      />
      <Prose>
        <p>
          Pick a method, fill the inputs (leave optional fields blank), and run. The shared result
          envelope — value, statistics, and the clauses it cites — is returned and rendered below.
        </p>
      </Prose>
      <Suspense fallback={<p className="text-[13px] muted">Loading playground…</p>}>
        <Playground />
      </Suspense>
    </div>
  );
}
