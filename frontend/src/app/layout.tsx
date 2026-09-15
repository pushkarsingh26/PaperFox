import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PaperFox — Job-Specific Resume Optimization Platform",
  description:
    "Production-ready resume optimization platform connecting candidate profiles with job-specific LaTeX generation.",
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
