export function DocsHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
}) {
  return (
    <header className="flex flex-col gap-3 border-b border-neutral-200 pb-6 dark:border-neutral-800">
      {eyebrow && (
        <span className="font-heading text-[11px] font-semibold uppercase tracking-wider text-primary-600 dark:text-primary-300">
          {eyebrow}
        </span>
      )}
      <h1 className="font-heading text-3xl font-semibold tracking-tight">{title}</h1>
      {description && <p className="text-[15px] leading-relaxed muted">{description}</p>}
    </header>
  );
}

export function Prose({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-5 text-[14px] leading-relaxed text-neutral-700 dark:text-neutral-300 [&_a]:text-primary-600 [&_a]:underline dark:[&_a]:text-primary-300 [&_code]:rounded [&_code]:bg-neutral-100 [&_code]:px-1 [&_code]:py-0.5 [&_code]:font-mono [&_code]:text-[12.5px] [&_h2]:mt-4 [&_h2]:font-heading [&_h2]:text-lg [&_h2]:font-semibold [&_h2]:text-neutral-900 dark:[&_code]:bg-neutral-800 dark:[&_h2]:text-white [&_ul]:flex [&_ul]:flex-col [&_ul]:gap-1.5 [&_ul]:pl-5 [&_ul]:list-disc">
      {children}
    </div>
  );
}
