import type { MetadataRoute } from "next";

const BASE_URL = "https://fair-value.ascent-partners.com";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/v1/", "/mcp"],
      },
    ],
    sitemap: `${BASE_URL}/sitemap.xml`,
  };
}
