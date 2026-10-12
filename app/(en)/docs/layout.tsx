import { DocsSidebar } from "@/components/docs/DocsSidebar";

export default function DocsLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="container-site grid gap-10 py-10 lg:grid-cols-[220px_1fr]">
      <aside className="hidden lg:block">
        <div className="sticky top-20 max-h-[calc(100vh-6rem)] overflow-y-auto pr-2 scroll-thin">
          <DocsSidebar />
        </div>
      </aside>
      <div className="min-w-0 max-w-3xl">{children}</div>
    </div>
  );
}
