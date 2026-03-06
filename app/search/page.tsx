import type { Metadata } from "next"
import { getPosts } from "@/lib/queries"
import { PostPreview } from "@/app/components/post-preview"
import { Pagination } from "@/app/components/pagination"
import { Intro } from "@/app/components/intro"
import SearchBar from "@/app/components/search-bar"
import { BLOG_NAME } from "@/lib/constants"
import { Search } from "lucide-react"

export const dynamic = "force-dynamic"

type PageProps = {
  searchParams: Promise<{ q?: string; page?: string }>
}

export async function generateMetadata({ searchParams }: PageProps): Promise<Metadata> {
  const { q } = await searchParams
  return {
    title: q ? `"${q}" - ${BLOG_NAME}` : `Search - ${BLOG_NAME}`,
  }
}

export default async function SearchPage({ searchParams }: PageProps) {
  const { q, page: pageParam } = await searchParams
  const currentPage = Number(pageParam) || 1

  const result = q
    ? await getPosts({ search: q, page: currentPage, perPage: 9 }, 0)
    : null

  return (
    <main>
      <div className="container mx-auto px-5 max-w-6xl">
        <Intro />

        <div className="max-w-md mt-8 mb-10">
          <h2 className="text-2xl font-black tracking-tight mb-4">Search</h2>
          <SearchBar />
        </div>

        {q && result && (
          <>
            <p className="text-sm text-muted-foreground mb-8">
              &ldquo;{q}&rdquo;
              {result.posts.length > 0
                ? ` - ${result.posts.length}건`
                : "에 대한 결과가 없습니다."}
            </p>

            {result.posts.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-10 mb-16">
                {result.posts.map((post) => (
                  <PostPreview key={post.id} post={post} />
                ))}
              </div>
            ) : (
              <div className="text-center py-20">
                <Search className="w-10 h-10 text-muted-foreground/20 mx-auto mb-3" />
                <p className="text-muted-foreground text-sm">다른 검색어를 시도해보세요.</p>
              </div>
            )}

            <Pagination
              currentPage={currentPage}
              totalPages={result.totalPages}
              basePath={`/search?q=${encodeURIComponent(q)}`}
            />
          </>
        )}

        {!q && (
          <div className="text-center py-20">
            <Search className="w-10 h-10 text-muted-foreground/20 mx-auto mb-3" />
            <p className="text-muted-foreground text-sm">검색어를 입력하세요.</p>
          </div>
        )}
      </div>
    </main>
  )
}
