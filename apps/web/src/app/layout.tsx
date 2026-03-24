import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Certified Massage Map",
  description: "국가 공인 안마원 위치 데이터를 수집하고 지도에 표시하는 프로젝트"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
