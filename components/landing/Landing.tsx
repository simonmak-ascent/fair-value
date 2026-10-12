import Image from "next/image";
import Link from "next/link";
import { LANDING_COPY, LANDING_STANDARDS, LOCALE_META, connectClients, hrefFor, locales, type Locale } from "@/lib/i18n";
import { ConnectTabs } from "@/components/landing/ConnectTabs";

const TOOLS_URL = "https://www.ascent-partners.com/tools";
const TECH_URL = "https://www.ascent-partners.com/services/technology-advisory";
const CONTACT_URL = "https://www.ascent-partners.com/about#contact";
const DOCS_URL = "/docs/getting-started";
const REPO_URL = "https://github.com/simonmak-ascent/fair-value";

function LocaleSwitcher({ locale, label }: { locale: Locale; label: string }) {
  return (
    <nav aria-label={label} className="flex items-center gap-1">
      {locales.map((l) => (
        <Link
          key={l}
          href={hrefFor(l, "/")}
          hrefLang={LOCALE_META[l].htmlLang}
          className={`rounded-full border px-2.5 py-1 text-[11px] font-semibold no-underline ${
            l === locale
              ? "border-primary-600 text-primary-600 dark:border-primary-300 dark:text-primary-300"
              : "border-neutral-200 text-neutral-500 dark:border-neutral-800 dark:text-neutral-400"
          }`}
        >
          {LOCALE_META[l].label}
        </Link>
      ))}
    </nav>
  );
}

export function Landing({ locale }: { locale: Locale }) {
  const c = LANDING_COPY[locale];
  const clients = connectClients();

  return (
    <div className="flex w-full min-w-0 flex-col">
      {/* Hero band — photographic + APG teal scrim + breadcrumb + H1 */}
      <header data-hero className="relative h-[180px] w-full overflow-hidden bg-primary-600 lg:h-[240px]">
        <Image src="/images/tool-valuation-mcp.jpg" alt="" fill priority sizes="100vw" className="object-cover" />
        <div aria-hidden className="absolute inset-0 bg-gradient-to-r from-primary-700/95 via-primary-700/50 to-transparent" />
        <nav aria-label="Breadcrumb" className="absolute inset-x-0 top-1">
          <ol className="container-site flex flex-wrap gap-2 py-1 text-[12px]">
            <li><a className="text-white/90 no-underline hover:underline" href="https://www.ascent-partners.com/">{c.crumbHome}</a></li>
            <li><a className="text-white/90 no-underline hover:underline" href={TOOLS_URL}>{c.crumbTools}</a></li>
            <li className="text-white" aria-current="page">{c.name}</li>
          </ol>
        </nav>
        <div className="absolute inset-x-0 bottom-0">
          <h1 className="container-site pb-4 text-[clamp(1.75rem,5vw,3.25rem)] font-black leading-[1.05] text-white lg:pb-6">
            {c.name}
          </h1>
        </div>
      </header>

      <div className="container-site flex flex-col items-center gap-10 py-14 lg:py-16">
        <header className="flex w-full max-w-2xl flex-col items-center gap-4 text-center">
          <span className="rounded-full bg-primary-600/10 px-3 py-1 text-[12px] font-semibold uppercase tracking-wide text-primary-600 dark:bg-primary-300/10 dark:text-primary-300">
            {c.type}
          </span>
          <p className="max-w-xl text-[18px] leading-relaxed text-neutral-600 dark:text-neutral-300">{c.value}</p>
          <p className="mt-1 border-s-2 border-secondary-300 ps-4 text-start text-[16px] italic text-neutral-900 dark:text-neutral-100">
            {c.thesis}
          </p>
        </header>

        <dl className="grid w-full max-w-3xl grid-cols-2 gap-4 sm:grid-cols-4">
          {c.stats.map((s) => (
            <div key={s.label} className="flex flex-col gap-1 rounded-md border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-900">
              <dt className="text-[14px] text-neutral-500 dark:text-neutral-400">{s.label}</dt>
              <dd className="font-heading text-[24px] font-bold text-primary-600 dark:text-primary-300">{s.value}</dd>
            </div>
          ))}
        </dl>

        <div className="flex w-full max-w-3xl flex-col gap-8">
          <section className="flex flex-col gap-3">
            <h2 className="font-heading text-[20px] font-bold text-primary-600 dark:text-primary-300">{c.capsHeading}</h2>
            <ul className="flex list-disc flex-col gap-2 ps-5">
              {c.capabilities.map((x) => (
                <li key={x} className="text-[16px] leading-relaxed text-neutral-700 dark:text-neutral-300">{x}</li>
              ))}
            </ul>
          </section>

          <section className="flex flex-col gap-3">
            <h2 className="font-heading text-[20px] font-bold text-primary-600 dark:text-primary-300">{c.standardsHeading}</h2>
            <ul className="flex flex-wrap gap-2">
              {LANDING_STANDARDS.map((s) => (
                <li key={s} className="rounded-full border border-neutral-200 bg-neutral-100 px-3 py-1 text-[12px] font-semibold text-neutral-900 dark:border-neutral-800 dark:bg-neutral-900 dark:text-neutral-100">
                  {s}
                </li>
              ))}
            </ul>
          </section>

          <section className="flex flex-col gap-4">
            <h2 className="font-heading text-[20px] font-bold text-primary-600 dark:text-primary-300">{c.connectHeading}</h2>
            <p className="text-[16px] leading-relaxed text-neutral-700 dark:text-neutral-300">{c.connectIntro}</p>
            <ConnectTabs clients={clients} copyLabel={c.copy} copiedLabel={c.copied} ariaLabel={c.connectHeading} />
          </section>

          <section className="flex flex-col gap-4">
            <h2 className="font-heading text-[20px] font-bold text-primary-600 dark:text-primary-300">{c.factsHeading}</h2>
            <dl className="flex flex-col gap-3">
              {c.facts.map((f) => (
                <div key={f.label} className="flex flex-col gap-1 sm:flex-row sm:items-baseline sm:gap-4">
                  <dt className="w-28 shrink-0 text-[14px] font-semibold uppercase tracking-wide text-neutral-900 dark:text-neutral-100">{f.label}</dt>
                  <dd className="break-all text-[16px] text-neutral-700 dark:text-neutral-300">
                    {f.code ? <code className="rounded bg-neutral-100 px-2 py-0.5 font-mono text-[14px] dark:bg-neutral-900">{f.value}</code> : f.value}
                  </dd>
                </div>
              ))}
            </dl>
          </section>

          <section className="flex flex-col gap-4 rounded-md border border-neutral-200 bg-white p-6 dark:border-neutral-800 dark:bg-neutral-900">
            <h2 className="font-heading text-[18px] font-bold text-primary-600 dark:text-primary-300">{c.originHeading}</h2>
            <p className="text-[16px] leading-relaxed text-neutral-700 dark:text-neutral-300">{c.originBody}</p>
            <div className="flex flex-wrap gap-4 text-[16px] font-semibold">
              <a className="text-primary-600 no-underline hover:underline dark:text-primary-300" href={TECH_URL}>{c.techLink}</a>
              <a className="text-primary-600 no-underline hover:underline dark:text-primary-300" href={CONTACT_URL}>{c.contact}</a>
            </div>
          </section>

          <div className="flex flex-wrap gap-3">
            <Link href={DOCS_URL} className="rounded-md bg-primary-600 px-6 py-2.5 text-[14px] font-semibold text-white transition-colors hover:bg-primary-700">
              {c.docs}
            </Link>
            <a href={REPO_URL} className="rounded-md border border-neutral-300 px-6 py-2.5 text-[14px] font-semibold text-neutral-900 transition-colors hover:bg-neutral-100 dark:border-neutral-700 dark:text-neutral-100 dark:hover:bg-neutral-900">
              {c.source}
            </a>
          </div>

          <Link href={TOOLS_URL} className="text-[14px] font-semibold text-primary-600 no-underline hover:underline dark:text-primary-300">
            ← {c.back}
          </Link>
        </div>
      </div>

      <div className="container-site flex justify-center pb-8">
        <LocaleSwitcher locale={locale} label={c.navLangLabel} />
      </div>
    </div>
  );
}
