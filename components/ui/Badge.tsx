import { cn } from "@/lib/utils";

const TONES: Record<string, string> = {
  neutral:
    "border-neutral-300 text-neutral-600 dark:border-neutral-700 dark:text-neutral-300",
  primary:
    "border-primary-300 bg-primary-50 text-primary-700 dark:border-primary-800 dark:bg-primary-950 dark:text-primary-300",
  gold: "border-secondary-300 bg-secondary-50 text-secondary-700 dark:border-secondary-800 dark:bg-secondary-950 dark:text-secondary-200",
  muted:
    "border-neutral-200 text-neutral-400 dark:border-neutral-800 dark:text-neutral-500",
};

export function Badge({
  children,
  tone = "neutral",
  title,
}: {
  children: React.ReactNode;
  tone?: keyof typeof TONES | string;
  title?: string;
}) {
  return (
    <span
      title={title}
      className={cn(
        "inline-flex items-center rounded border px-1.5 py-0.5 font-mono text-[11px] leading-none",
        TONES[tone] ?? TONES.neutral,
      )}
    >
      {children}
    </span>
  );
}
