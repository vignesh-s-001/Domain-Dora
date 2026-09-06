import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { Providers } from "@/components/providers";
import { ThemeProvider } from "@/components/theme-provider";
import { CornerAccents } from "@/components/CornerAccents";
import { BuyMeCoffee } from "@/components/BuyMeCoffee";
import GoogleAnalytics from "@/components/GoogleAnalytics";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const playfair = Playfair_Display({ subsets: ["latin"], variable: "--font-playfair" });

export const metadata: Metadata = {
  title: "Domain-Dora | Premium Domain Intelligence",
  description: "Understand what's behind any domain. Explore domain registration, DNS infrastructure, SSL certificates, IP networks, and more.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <Script id="google-tag-manager" strategy="afterInteractive">
          {`
            (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
            new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
            j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
            'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
            })(window,document,'script','dataLayer','GTM-527CPBP4');
          `}
        </Script>
      </head>
      <body className={`${inter.variable} ${playfair.variable} font-sans antialiased bg-neutral-50 dark:bg-neutral-950 text-neutral-900 dark:text-neutral-50 min-h-screen selection:bg-blue-500/30 transition-colors duration-300 relative`}>
        <noscript>
          <iframe
            src="https://www.googletagmanager.com/ns.html?id=GTM-527CPBP4"
            height="0"
            width="0"
            style={{ display: "none", visibility: "hidden" }}
          ></iframe>
        </noscript>
        {/* Premium ambient glow background for Dark Mode */}
        <div className="fixed inset-0 z-[-1] h-full w-full hidden dark:block bg-neutral-950 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(78,105,196,0.15),rgba(0,0,0,0))]"></div>
        {/* Premium subtle gradient for Light Mode */}
        <div className="fixed inset-0 z-[-1] h-full w-full block dark:hidden bg-neutral-50 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(78,105,196,0.08),rgba(255,255,255,0))]"></div>

        <CornerAccents />

        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
          <Providers>
            <GoogleAnalytics />
            {children}
            <BuyMeCoffee />
          </Providers>
        </ThemeProvider>
      </body>
    </html>
  );
}
