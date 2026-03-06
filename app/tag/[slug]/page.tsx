import { notFound } from "next/navigation"
import type { Metadata } from "next"
import { getTagBySlug, getPosts } from "@/lib/queries"
import { PostPreview } from "@/app/components/post-preview"
import { Pagination } from "@/app/components/pagination"
import { Intro } from "@/app/components/intro"
import { BLOG_NAME } from "@/lib/constants"

export const revalidate = 120

type PageProps = {
  params: Promise<{ slug: string }>
  searchParams: Promise<{ page?: string }>
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params
  const tag = await getTagBySlug(slug)
  if (!tag) return {}
  return {
    title: `#${tag.name} - ${BLOG_NAME}`,
    description: `#${tag.name} 태그가 포함된 글 목록`,
  }
}

export default async function TagPage({ params, searchParams }: PageProps) {
  const { slug } = await params
  const { page: pageParam } = await searchParams
  const currentPage = Number(pageParam) || 1

  const tag = await getTagBySlug(slug)
  if (!tag) notFound()

  const { posts, totalPages } = await getPosts({
    tag: tag.id,
    page: currentPage,
    perPage: 9,
  })

  return (
    <main>
      <div className="container mx-auto px-5 max-w-6xl">
        <Intro />

        <div className="mb-10 mt-8">
          <h2 className="text-2xl md:text-3xl font-black tracking-tight">
            #{tag.name}
          </h2>
        </div>

        {posts.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-10 mb-16">
            {posts.map((post) => (
              <PostPreview key={post.id} post={post} />
            ))}
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-20 text-lg">
            이 태그에 해당하는 글이 없습니다.
          </p>
        )}

        <Pagination currentPage={currentPage} totalPages={totalPages} basePath={`/tag/${slug}`} />
      </div>
    </main>
  )
}
