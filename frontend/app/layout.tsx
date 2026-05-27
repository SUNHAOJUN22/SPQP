import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "硅氧键催化量子研究平台",
  description: "面向中文科研用户的 Si–O 键、TEA 助催化剂、Ti 毒化判据与插入反应能量面研究平台。"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
