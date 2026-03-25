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
    <section className="mb-10">
      <h2 className="text-xl font-extrabold tracking-tight mb-4">
        주제별
      </h2>
      <div className="flex flex-wrap gap-2">
        <CategoryPill href="/" active={!activeSlug}>
          전체
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
      </div>
    </section>
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
        "whitespace-nowrap px-4 py-2 text-sm font-semibold rounded-full transition-colors",
        active
          ? "bg-foreground text-background"
          : "bg-muted text-muted-foreground hover:bg-foreground/10 hover:text-foreground"
      )}
    >
      {children}
    </Link>
  )
}
