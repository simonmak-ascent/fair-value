export { metadata } from "@/components/layout/RootShell";
import { RootShell } from "@/components/layout/RootShell";

export default function ZhLayout({ children }: { children: React.ReactNode }) {
  return <RootShell lang="zh-Hans">{children}</RootShell>;
}
