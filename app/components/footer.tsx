import Link from "next/link"
import { BLOG_NAME, BLOG_DESCRIPTION } from "@/lib/constants"
import { BarChart3 } from "lucide-react"

export default function Footer() {
  return (
    <footer className="border-t bg-card">
      <div className="container mx-auto px-5 max-w-6xl">
        <div className="py-10 md:py-14">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div>
              <Link href="/" className="inline-flex items-center gap-2 mb-2">
                <BarChart3 className="w-4 h-4 text-primary" />
                <span className="text-sm font-black tracking-tight">{BLOG_NAME}</span>
              </Link>
              <p className="text-xs text-muted-foreground max-w-xs">
                {BLOG_DESCRIPTION}. 투자 판단은 본인의 몫이며, 이 블로그는 종목 추천을 하지 않습니다.
              </p>
            </div>
            <nav className="flex gap-5 text-xs font-medium text-muted-foreground">
              <Link href="/" className="hover:text-foreground transition-colors">
                Home
              </Link>
              <Link href="/search" className="hover:text-foreground transition-colors">
                Search
              </Link>
            </nav>
          </div>
          <div className="mt-8 pt-6 border-t">
            <p className="text-[11px] text-muted-foreground">
              &copy; {new Date().getFullYear()} {BLOG_NAME}. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
