import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth/authContext";
import { AccessibilityProvider } from "@/components/common/AccessibilityProvider";
import { Toaster } from "@/components/ui/toaster";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Pro Forma Analytics",
  description: "Modern real estate financial analysis dashboard",
  keywords: ["real estate", "DCF", "financial analysis", "investment", "Monte Carlo"],
  authors: [{ name: "Pro Forma Analytics" }],
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased">
        <AccessibilityProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </AccessibilityProvider>
        <Toaster />
      </body>
    </html>
  );
}
