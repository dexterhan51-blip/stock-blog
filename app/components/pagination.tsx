import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"

export function Pagination({
  currentPage,
  totalPages,
  basePath,
}: {
  currentPage: number
  totalPages: number
  basePath: string
}) {
  if (totalPages <= 1) return null

  const pages = Array.from({ length: totalPages }, (_, i) => i + 1)
  const separator = basePath.includes("?") ? "&" : "?"

  return (
    <nav className="flex items-center justify-center gap-2 my-16">
      {currentPage > 1 && (
        <Link href={`${basePath}${separator}page=${currentPage - 1}`}>
          <Button variant="outline" size="icon">
            <ChevronLeft className="h-4 w-4" />
          </Button>
        </Link>
      )}

      {pages.map((page) => (
        <Link key={page} href={`${basePath}${separator}page=${page}`}>
          <Button
            variant={page === currentPage ? "default" : "outline"}
            size="sm"
          >
            {page}
          </Button>
        </Link>
      ))}

      {currentPage < totalPages && (
        <Link href={`${basePath}${separator}page=${currentPage + 1}`}>
          <Button variant="outline" size="icon">
            <ChevronRight className="h-4 w-4" />
          </Button>
        </Link>
      )}
    </nav>
  )
}
