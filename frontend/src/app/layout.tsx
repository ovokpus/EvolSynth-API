import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "EvolSynth - Advanced Synthetic Data Generation",
  description: "Transform your documents into sophisticated evaluation datasets with intelligent question evolution, concurrent processing, and comprehensive quality assessment.",
  keywords: ["AI", "synthetic data", "LangGraph", "Evol-Instruct", "question generation", "evaluation datasets"],
  authors: [{ name: "Ovo Okpubuluku" }],
  openGraph: {
    title: "EvolSynth - Advanced Synthetic Data Generation",
    description: "Revolutionary AI-powered synthetic data generation using LangGraph-based Evol-Instruct methodology",
    type: "website",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "EvolSynth - Advanced Synthetic Data Generation",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "EvolSynth - Advanced Synthetic Data Generation",
    description: "Revolutionary AI-powered synthetic data generation using LangGraph-based Evol-Instruct methodology",
    images: ["/og-image.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth" style={{ colorScheme: 'light', backgroundColor: '#ffffff' }}>
      <head>
        <style dangerouslySetInnerHTML={{
          __html: `
            * { 
              color-scheme: light !important; 
            }
            html { 
              background-color: #ffffff !important; 
              color: #7c3aed !important;
            }
            body { 
              background: linear-gradient(135deg, #ffffff 0%, #faf5ff 30%, #f3e8ff 100%) !important;
              color: #7c3aed !important;
              min-height: 100vh !important;
            }
            h1, h2, h3, h4, h5, h6, p, span, div, label {
              color: #7c3aed !important;
            }
          `
        }} />
      </head>
      <body
        className={`${inter.variable} font-sans antialiased min-h-screen text-primary-700 bg-white`}
        style={{ 
          background: 'linear-gradient(135deg, #ffffff 0%, #faf5ff 30%, #f3e8ff 100%) !important',
          minHeight: '100vh',
          color: '#7c3aed !important'
        }}
      >
        <div className="relative min-h-screen bg-white" style={{ backgroundColor: '#ffffff !important' }}>
          {/* Light background effects */}
          <div className="fixed inset-0 bg-gradient-to-br from-purple-100/20 via-transparent to-purple-200/15" />
          <div className="fixed inset-0 bg-[url('/grid.svg')] opacity-5" />
          
          {/* Content */}
          <div className="relative z-10 bg-transparent">
            {children}
          </div>
        </div>
      </body>
    </html>
  );
}
