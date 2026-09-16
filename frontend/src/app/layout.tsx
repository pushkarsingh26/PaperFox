import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "https://paperfox.app"),
  title: "PaperFox — AI-Powered Job-Specific Resume Optimization",
  description:
    "Turn every job description into a tailored, evidence-grounded, single-page ATS resume with deterministic LaTeX rendering and factual verification.",
  icons: {
    icon: [
      { url: "/branding/favicon.png", sizes: "128x128", type: "image/png" },
      { url: "/favicon.ico" },
    ],
    apple: "/branding/favicon.png",
  },
  openGraph: {
    title: "PaperFox — AI-Powered Job-Specific Resume Optimization",
    description: "Turn every job description into a tailored, evidence-grounded, single-page ATS resume.",
    siteName: "PaperFox",
    images: [
      {
        url: "/assets/paperfox-cover.png",
        width: 1600,
        height: 900,
        alt: "PaperFox — AI-Powered Job-Specific Resume Optimization",
      },
    ],
    locale: "en_US",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-slate-950 text-slate-100 antialiased selection:bg-amber-500/30 selection:text-amber-200`}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
