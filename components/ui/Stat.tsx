export function Stat({
  value,
  label,
  accent = false,
}: {
  value: string | number;
  label: string;
  accent?: boolean;
}) {
  return (
    <div className="flex flex-col gap-1">
      <span
        className={`font-heading text-2xl font-semibold tabular-nums ${
          accent ? "text-primary-600 dark:text-primary-300" : ""
        }`}
      >
        {value}
      </span>
      <span className="text-[12px] uppercase tracking-wide text-neutral-500 dark:text-neutral-400">
        {label}
      </span>
    </div>
  );
}
