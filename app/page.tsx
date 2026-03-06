import { Intro } from "./components/intro"
import { HeroPost } from "./components/hero-post"
import { MoreStories } from "./components/more-stories"
import { CategoryNav } from "./components/category-nav"
import { Pagination } from "./components/pagination"
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
    getPosts({ page: currentPage, perPage: 10 }),
    getCategories(),
  ])

  const heroPost = currentPage === 1 ? posts[0] : undefined
  const morePosts = currentPage === 1 ? posts.slice(1) : posts

  return (
    <main>
      <div className="container mx-auto px-5 max-w-6xl">
        <Intro />
        <CategoryNav categories={categories} />
        {heroPost && <HeroPost post={heroPost} />}
        {morePosts.length > 0 && (
          <MoreStories posts={morePosts} title="Latest" />
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
