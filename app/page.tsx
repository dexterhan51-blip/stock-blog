import { Intro } from "./components/intro"
import { HeroPost } from "./components/hero-post"
import { FeaturedPosts } from "./components/featured-posts"
import { MoreStories } from "./components/more-stories"
import { CategoryNav } from "./components/category-nav"
import { Pagination } from "./components/pagination"
import { YoutubeShorts } from "./components/youtube-shorts"
import { getPosts, getCategories } from "@/lib/queries"
import type { Metadata } from "next"
import { BLOG_NAME, BLOG_DESCRIPTION, SITE_URL } from "@/lib/constants"

export const revalidate = 60

export const metadata: Metadata = {
  title: BLOG_NAME,
  description: BLOG_DESCRIPTION,
  openGraph: {
    title: BLOG_NAME,
    description: BLOG_DESCRIPTION,
    url: SITE_URL,
    siteName: BLOG_NAME,
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: BLOG_NAME,
    description: BLOG_DESCRIPTION,
  },
}

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>
}) {
  const { page: pageParam } = await searchParams
  const currentPage = Number(pageParam) || 1

  const [{ posts, totalPages }, categories] = await Promise.all([
    getPosts({ page: currentPage, perPage: 13 }),
    getCategories(),
  ])

  const isFirstPage = currentPage === 1
  const heroPost = isFirstPage ? posts[0] : undefined
  const featuredPosts = isFirstPage ? posts.slice(1, 5) : []
  const restPosts = isFirstPage ? posts.slice(5) : posts

  return (
    <main>
      <div className="container mx-auto px-5 max-w-6xl">
        <Intro />

        {/* 1. 히어로 — 최신글 1개 */}
        {heroPost && <HeroPost post={heroPost} />}

        {/* 2. 추천 글 — 다음 최신 4개 */}
        {featuredPosts.length > 0 && <FeaturedPosts posts={featuredPosts} />}

        {/* 3. 클립 영상 — 유튜브 쇼츠 */}
        {isFirstPage && <YoutubeShorts />}

        {/* 4. 주제별 — 카테고리 태그 */}
        <CategoryNav categories={categories} />

        {/* 5. 전체 글 — 나머지 3열 그리드 */}
        {restPosts.length > 0 && (
          <MoreStories posts={restPosts} title="전체 글" />
        )}

        {posts.length === 0 && (
          <div className="text-center py-20">
            <p className="text-muted-foreground text-lg">
              아직 발행된 글이 없습니다.
            </p>
          </div>
        )}
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          basePath="/"
        />
      </div>
    </main>
  )
}
