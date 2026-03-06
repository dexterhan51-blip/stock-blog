import Link from "next/link"
import type { Category } from "@/lib/types"
import { cn } from "@/lib/utils"

export function CategoryNav({
  categories,
  activeSlug,
}: {
  categories: Category[]
  activeSlug?: string
}) {
  return (
    <nav className="flex gap-1.5 overflow-x-auto py-4 mb-8 scrollbar-hide">
      <CategoryPill href="/" active={!activeSlug}>
        All
      </CategoryPill>
      {categories.map((category) => (
        <CategoryPill
          key={category.id}
          href={`/category/${category.slug}`}
          active={activeSlug === category.slug}
        >
          {category.name}
        </CategoryPill>
      ))}
    </nav>
  )
}

function CategoryPill({
  href,
  active,
  children,
}: {
  href: string
  active: boolean
  children: React.ReactNode
}) {
  return (
    <Link
      href={href}
      className={cn(
        "whitespace-nowrap px-4 py-1.5 text-xs font-bold rounded-full transition-colors tracking-wide uppercase",
        active
          ? "bg-foreground text-background"
          : "bg-muted text-muted-foreground hover:bg-foreground/10 hover:text-foreground"
      )}
    >
      {children}
    </Link>
  )
}
