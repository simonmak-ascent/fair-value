export { metadata } from "@/components/layout/RootShell";
import { RootShell } from "@/components/layout/RootShell";

export default function HkLayout({ children }: { children: React.ReactNode }) {
  return <RootShell lang="zh-Hant-HK">{children}</RootShell>;
}
