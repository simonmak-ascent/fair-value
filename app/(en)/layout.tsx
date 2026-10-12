export { metadata } from "@/components/layout/RootShell";
import { RootShell } from "@/components/layout/RootShell";

export default function EnLayout({ children }: { children: React.ReactNode }) {
  return <RootShell lang="en-GB">{children}</RootShell>;
}
