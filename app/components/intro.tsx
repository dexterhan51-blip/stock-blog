import Link from "next/link"
import { BLOG_NAME, BLOG_DESCRIPTION } from "@/lib/constants"
import { ThemeToggle } from "./theme-toggle"
import SearchBar from "./search-bar"
import { BarChart3, Search } from "lucide-react"

export function Intro() {
  return (
    <header className="border-b border-border">
      <div className="flex items-center justify-between py-5">
        <Link href="/" className="group flex items-center gap-2.5">
          <div className="flex items-center justify-center w-9 h-9 rounded-md bg-primary text-primary-foreground">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-black tracking-tight leading-none">
              {BLOG_NAME}
            </h1>
            <p className="text-xs text-muted-foreground mt-0.5 hidden sm:block">
              {BLOG_DESCRIPTION}
            </p>
          </div>
        </Link>
        <div className="flex items-center gap-2">
          <Link
            href="/search"
            className="md:hidden flex items-center justify-center w-9 h-9 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          >
            <Search className="w-4 h-4" />
          </Link>
          <div className="hidden md:block">
            <SearchBar />
          </div>
          <ThemeToggle />
        </div>
      </div>
    </header>
  )
}
