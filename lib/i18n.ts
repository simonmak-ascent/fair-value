// Locale registry + landing copy for the fair-value frontage.
// Locales mirror the Ascent Partners site: en (default, no prefix), zh (/zh), hk (/hk).

export const locales = ["en", "zh", "hk"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "en";

export const LOCALE_META: Record<Locale, { htmlLang: string; label: string; prefix: string }> = {
  en: { htmlLang: "en-GB", label: "English", prefix: "" },
  zh: { htmlLang: "zh-Hans", label: "中文", prefix: "/zh" },
  hk: { htmlLang: "zh-Hant-HK", label: "繁體", prefix: "/hk" },
};

export function isLocale(value: string): value is Locale {
  return (locales as readonly string[]).includes(value);
}

export interface LandingCopy {
  type: string;
  name: string;
  value: string;
  thesis: string;
  stats: { value: string; label: string }[];
  capsHeading: string;
  capabilities: string[];
  standardsHeading: string;
  connectHeading: string;
  connectIntro: string;
  factsHeading: string;
  facts: { label: string; value: string; code?: boolean }[];
  originHeading: string;
  originBody: string;
  techLink: string;
  contact: string;
  docs: string;
  source: string;
  back: string;
  copy: string;
  copied: string;
  crumbHome: string;
  crumbTools: string;
  navLangLabel: string;
}

const ENDPOINT = "https://fair-value.ascent-partners.com/mcp";
const REGISTRY = "io.github.simonmak-ascent/fair-value";

export const LANDING_COPY: Record<Locale, LandingCopy> = {
  en: {
    type: "MCP server + REST API",
    name: "Fair Value",
    value:
      "Give AI agents a deterministic, IVS/IFRS-cited valuation engine for company and financial-instrument valuations.",
    thesis:
      "A valuation is an argument. This is the one we make — deterministic, and cited to the standards a reviewer will check.",
    stats: [
      { value: "135", label: "valuation methods" },
      { value: "14", label: "MCP tools" },
      { value: "120", label: "methods cited" },
      { value: "Open", label: "no API key" },
    ],
    capsHeading: "Capabilities",
    capabilities: [
      "135 methods across 14 tools — DCF, market, cost of capital, options, fixed income, credit, actuarial",
      "Every method maps to verbatim IVS 2025 / IFRS / IAS clauses",
      "Deterministic-first; stochastic methods return the distribution and accept a seed",
      "One registry, three surfaces: MCP, versioned /v1 REST, and the Python facade",
    ],
    standardsHeading: "Standards",
    connectHeading: "Connect",
    connectIntro: "Point an MCP client at the hosted endpoint. Open access, no API key.",
    factsHeading: "Facts",
    facts: [
      { label: "Endpoint", value: ENDPOINT, code: true },
      { label: "Transport", value: "Streamable HTTP" },
      { label: "Auth", value: "Open — no API key" },
      { label: "Licence", value: "MIT" },
      { label: "Registry", value: REGISTRY, code: true },
    ],
    originHeading: "Where it comes from",
    originBody:
      "Built by the Ascent Partners technology practice — the machinery behind our valuation numbers, opened for inspection.",
    techLink: "Technology Advisory",
    contact: "Contact us",
    docs: "Documentation",
    source: "Source",
    back: "All tools",
    copy: "Copy",
    copied: "Copied",
    crumbHome: "Home",
    crumbTools: "Open Tooling",
    navLangLabel: "Language",
  },
  zh: {
    type: "MCP 服务器 + REST API",
    name: "Fair Value",
    value: "为 AI 代理提供确定性的、引用 IVS/IFRS 的企业及金融工具估值引擎。",
    thesis: "估值是一场论证。这就是我们所做的论证——确定，且引用复核者会查证的准则。",
    stats: [
      { value: "135", label: "种估值方法" },
      { value: "14", label: "个 MCP 工具" },
      { value: "120", label: "种方法已引用" },
      { value: "开放", label: "无需密钥" },
    ],
    capsHeading: "能力",
    capabilities: [
      "14 个工具、135 种方法——DCF、市场法、资本成本、期权、固定收益、信用、精算",
      "每种方法均映射至逐字引用的 IVS 2025 / IFRS / IAS 条款",
      "确定性优先；随机方法返回分布并可设定随机种子",
      "同一注册表，三种界面：MCP、版本化 /v1 REST 及 Python 门面",
    ],
    standardsHeading: "准则",
    connectHeading: "连接",
    connectIntro: "将 MCP 客户端指向托管端点。开放访问，无需 API 密钥。",
    factsHeading: "信息",
    facts: [
      { label: "端点", value: ENDPOINT, code: true },
      { label: "传输", value: "Streamable HTTP" },
      { label: "认证", value: "开放——无需密钥" },
      { label: "许可", value: "MIT" },
      { label: "注册表", value: REGISTRY, code: true },
    ],
    originHeading: "来源",
    originBody: "由艾升集团技术咨询团队构建——我们估值数字背后的机器，开放以供检视。",
    techLink: "技术咨询",
    contact: "联系我们",
    docs: "文档",
    source: "源代码",
    back: "全部工具",
    copy: "复制",
    copied: "已复制",
    crumbHome: "首页",
    crumbTools: "开放工具",
    navLangLabel: "语言",
  },
  hk: {
    type: "MCP 伺服器 + REST API",
    name: "Fair Value",
    value: "為 AI 代理提供確定性的、引用 IVS/IFRS 的企業及金融工具估值引擎。",
    thesis: "估值是一場論證。這就是我們所做的論證——確定，且引用覆核者會查證的準則。",
    stats: [
      { value: "135", label: "種估值方法" },
      { value: "14", label: "個 MCP 工具" },
      { value: "120", label: "種方法已引用" },
      { value: "開放", label: "無需密鑰" },
    ],
    capsHeading: "能力",
    capabilities: [
      "14 個工具、135 種方法——DCF、市場法、資本成本、期權、固定收益、信用、精算",
      "每種方法均映射至逐字引用的 IVS 2025 / IFRS / IAS 條款",
      "確定性優先；隨機方法返回分佈並可設定隨機種子",
      "同一註冊表，三種界面：MCP、版本化 /v1 REST 及 Python 門面",
    ],
    standardsHeading: "準則",
    connectHeading: "連接",
    connectIntro: "將 MCP 客戶端指向託管端點。開放存取，無需 API 密鑰。",
    factsHeading: "資訊",
    facts: [
      { label: "端點", value: ENDPOINT, code: true },
      { label: "傳輸", value: "Streamable HTTP" },
      { label: "認證", value: "開放——無需密鑰" },
      { label: "授權", value: "MIT" },
      { label: "註冊表", value: REGISTRY, code: true },
    ],
    originHeading: "來源",
    originBody: "由艾升集團技術諮詢團隊構建——我們估值數字背後的機器，開放以供檢視。",
    techLink: "技術諮詢",
    contact: "聯絡我們",
    docs: "文件",
    source: "原始碼",
    back: "全部工具",
    copy: "複製",
    copied: "已複製",
    crumbHome: "首頁",
    crumbTools: "開放工具",
    navLangLabel: "語言",
  },
};

export const LANDING_STANDARDS = ["IVS 2025", "IFRS 13", "IFRS 9", "IAS 36"];

export function hrefFor(locale: Locale, path: string): string {
  const clean = path === "/" ? "" : path.startsWith("/") ? path : `/${path}`;
  return `${LOCALE_META[locale].prefix}${clean}` || "/";
}

export interface ConnectClient {
  key: string;
  label: string;
  code: string;
}

/** Per-client connect snippets — generated from the endpoint, never hand-written. */
export function connectClients(): ConnectClient[] {
  const key = "fair-value";
  const json = (o: unknown) => JSON.stringify(o, null, 2);
  const servers = json({ mcpServers: { [key]: { url: ENDPOINT } } });
  return [
    { key: "opencode", label: "OpenCode", code: json({ $schema: "https://opencode.ai/config.json", mcp: { [key]: { type: "remote", url: ENDPOINT } } }) },
    { key: "claude-code", label: "Claude Code", code: `claude mcp add --transport http ${key} ${ENDPOINT}` },
    { key: "claude-desktop", label: "Claude Desktop", code: servers },
    { key: "cursor", label: "Cursor", code: servers },
    { key: "vscode", label: "VS Code", code: json({ servers: { [key]: { type: "http", url: ENDPOINT } } }) },
    { key: "generic", label: "Any MCP client", code: servers },
  ];
}
