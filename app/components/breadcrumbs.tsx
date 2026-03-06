import Link from "next/link"
import { ChevronRight } from "lucide-react"

interface BreadcrumbItem {
  label: string
  href?: string
}

export function Breadcrumbs({ items }: { items: BreadcrumbItem[] }) {
  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-sm text-muted-foreground mb-8">
      <Link href="/" className="hover:text-primary transition-colors">
        홈
      </Link>
      {items.map((item, index) => (
        <span key={index} className="flex items-center gap-1">
          <ChevronRight className="h-3 w-3" />
          {item.href ? (
            <Link href={item.href} className="hover:text-primary transition-colors">
              {item.label}
            </Link>
          ) : (
            <span className="text-foreground truncate max-w-[200px]">{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  )
}
