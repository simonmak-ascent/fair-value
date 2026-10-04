import raw from "@/data/catalog.json";

export interface MethodInput {
  name: string;
  type: string;
  description?: string;
  enum?: string[];
}

export interface Citation {
  id: string;
  standard: string;
  label: string;
  summary: string;
}

export interface Method {
  tool: string;
  method: string;
  summary: string;
  formula_ref: string;
  approach: string;
  solution_type: string;
  standards: string[];
  inputs: MethodInput[];
  required: string[];
  citations: Citation[];
  risks: string[];
  implemented: boolean;
}

export interface Clause {
  id: string;
  standard: string;
  label: string;
  summary: string;
  text: string;
  cited_by: string[];
}

export interface StandardRef {
  id: string;
  title: string;
  family: string;
  edition: string;
  source_ref: string;
}

export interface Tool {
  id: string;
  title: string;
  description: string;
  surface: string;
  methods: string[];
}

export interface Catalog {
  surface_version: string;
  generated_from: string;
  counts: {
    tools: number;
    methods: number;
    implemented: number;
    deferred: number;
    cited: number;
    uncited: number;
    orphan_clauses: number;
    clauses: number;
  };
  standards: StandardRef[];
  clauses: Clause[];
  tools: Tool[];
  methods: Method[];
}

export const catalog = raw as Catalog;

export const methods: Method[] = catalog.methods;
export const tools: Tool[] = catalog.tools;
export const clauses: Clause[] = catalog.clauses;
export const standards: StandardRef[] = catalog.standards;
export const counts = catalog.counts;

const byMethod = new Map(methods.map((m) => [m.method, m]));
const byClause = new Map(clauses.map((c) => [c.id, c]));

export function getMethod(method: string): Method | undefined {
  return byMethod.get(method);
}

export function getClause(id: string): Clause | undefined {
  return byClause.get(id);
}

export function methodHref(method: string): string {
  return `/docs/methods/${method}`;
}

export function clauseHref(id: string): string {
  return `/docs/standards#${id}`;
}
