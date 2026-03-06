"use client"

import { useRouter } from "next/navigation"
import { useState, useCallback, useRef, useEffect } from "react"
import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"

export default function SearchBar() {
  const router = useRouter()
  const [query, setQuery] = useState("")
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const handleSearch = useCallback(
    (value: string) => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
      debounceRef.current = setTimeout(() => {
        if (value.trim()) {
          router.push(`/search?q=${encodeURIComponent(value.trim())}`)
        }
      }, 500)
    },
    [router]
  )

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [])

  return (
    <div className="relative w-full md:w-56 lg:w-64">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input
        placeholder="검색..."
        value={query}
        onChange={(e) => {
          setQuery(e.target.value)
          handleSearch(e.target.value)
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter" && query.trim()) {
            if (debounceRef.current) clearTimeout(debounceRef.current)
            router.push(`/search?q=${encodeURIComponent(query.trim())}`)
          }
        }}
        className="pl-9 h-9 text-sm bg-muted/50 border-transparent focus:border-border focus:bg-background"
      />
    </div>
  )
}
