import type { MetadataRoute } from "next";

import { methodHref, methods } from "@/lib/catalog";

const BASE_URL = "https://fair-value.ascent-partners.com";

const STATIC_PAGES: Array<[string, number]> = [
  ["", 1],
  ["/docs", 0.9],
  ["/docs/getting-started", 0.8],
  ["/docs/mcp", 0.8],
  ["/docs/api", 0.8],
  ["/docs/hosting", 0.7],
  ["/docs/methods", 0.8],
  ["/docs/examples", 0.7],
  ["/docs/playground", 0.7],
  ["/docs/standards", 0.7],
  ["/docs/status", 0.5],
  ["/docs/slo", 0.4],
  ["/docs/changelog", 0.4],
];

export default function sitemap(): MetadataRoute.Sitemap {
  const pages: MetadataRoute.Sitemap = STATIC_PAGES.map(([path, priority]) => ({
    url: `${BASE_URL}${path}`,
    lastModified: new Date(),
    changeFrequency: path === "" ? "weekly" : "monthly",
    priority,
  }));

  const methodPages: MetadataRoute.Sitemap = methods.map((m) => ({
    url: `${BASE_URL}${methodHref(m.method)}`,
    lastModified: new Date(),
    changeFrequency: "monthly",
    priority: 0.6,
  }));

  return [...pages, ...methodPages];
}
