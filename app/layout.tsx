import type React from "react"
import { Noto_Sans_KR } from "next/font/google"
import Footer from "./components/footer"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { BLOG_NAME, BLOG_DESCRIPTION } from "@/lib/constants"

const notoSansKR = Noto_Sans_KR({
  subsets: ["latin"],
  weight: ["400", "500", "700", "900"],
  display: "swap",
})

export const metadata = {
  title: {
    default: BLOG_NAME,
    template: `%s | ${BLOG_NAME}`,
  },
  description: BLOG_DESCRIPTION,
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className={`${notoSansKR.className} min-h-screen flex flex-col`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="flex-1">
            {children}
          </div>
          <Footer />
        </ThemeProvider>
      </body>
    </html>
  )
}
