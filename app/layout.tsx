import type { Metadata } from "next";
import { Open_Sans, Titillium_Web, Raleway, JetBrains_Mono } from "next/font/google";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import "@/app/globals.css";

const openSans = Open_Sans({ subsets: ["latin"], variable: "--font-open-sans", display: "swap" });
const titillium = Titillium_Web({
  subsets: ["latin"],
  weight: ["400", "600", "700"],
  variable: "--font-titillium",
  display: "swap",
});
const raleway = Raleway({ subsets: ["latin"], variable: "--font-raleway", display: "swap" });
const jetbrains = JetBrains_Mono({ subsets: ["latin"], variable: "--font-jetbrains-mono", display: "swap" });

const siteUrl = "https://fair-value.ascent-partners.com";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "fair-value — valuation MCP server & REST API",
    template: "%s · fair-value",
  },
  description:
    "138 valuation methods across 16 MCP tools, cited to IVS 2025 and IFRS/IAS. Deterministic-first results with statistics and verbatim standard citations, over MCP and REST.",
  keywords: [
    "valuation",
    "DCF",
    "IVS 2025",
    "IFRS 13",
    "MCP server",
    "Model Context Protocol",
    "REST API",
    "fair value",
    "credit risk",
    "derivatives",
  ],
  authors: [{ name: "Ascent Partners Group Ltd" }],
  openGraph: {
    title: "fair-value — valuation MCP server & REST API",
    description: "138 valuation methods, cited to IVS 2025 / IFRS-IAS, over MCP and REST.",
    type: "website",
    siteName: "fair-value",
    url: siteUrl,
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${openSans.variable} ${titillium.variable} ${raleway.variable} ${jetbrains.variable}`}
    >
      <body className="flex min-h-screen flex-col">
        <script
          dangerouslySetInnerHTML={{
            __html:
              "try{var t=localStorage.getItem('theme');var d=t?t==='dark':true;if(d)document.documentElement.classList.add('dark');}catch(e){document.documentElement.classList.add('dark');}",
          }}
        />
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
