export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

export function titleCase(value: string): string {
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function methodLabel(method: string): string {
  return titleCase(method);
}

export function toolLabel(tool: string): string {
  return titleCase(tool.replace(/^calculate_/, ""));
}

/** Render a TS-ish preview value for a method input (playground + examples). */
export function sampleValue(type: string, name: string): unknown {
  const t = type.toLowerCase();
  if (t.includes("array") || t.includes("nums")) {
    return name === "cash_flows" ? [100, 110, 121] : [1, 2, 3];
  }
  if (t.includes("object")) return {};
  if (t.includes("bool")) return true;
  if (t.includes("int")) return 5;
  if (t.includes("number")) {
    if (name.includes("rate") || name.includes("yield") || name.includes("wacc")) return 0.1;
    if (name.includes("growth")) return 0.03;
    if (name.includes("beta")) return 1.1;
    if (name.includes("tax")) return 0.16;
    return 100;
  }
  return name.includes("method") ? "" : "value";
}
