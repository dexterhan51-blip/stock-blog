import { notFound } from "next/navigation"
import type { Metadata } from "next"
import { getCategoryBySlug, getCategories, getPosts } from "@/lib/queries"
import { PostPreview } from "@/app/components/post-preview"
import { CategoryNav } from "@/app/components/category-nav"
import { Pagination } from "@/app/components/pagination"
import { Intro } from "@/app/components/intro"
import { BLOG_NAME } from "@/lib/constants"

export const revalidate = 120

export async function generateStaticParams() {
  const categories = await getCategories()
  return categories.map((cat) => ({ slug: cat.slug }))
}

type PageProps = {
  params: Promise<{ slug: string }>
  searchParams: Promise<{ page?: string }>
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params
  const category = await getCategoryBySlug(slug)
  if (!category) return {}
  return {
    title: `${category.name} - ${BLOG_NAME}`,
    description: category.description || `${category.name} 카테고리의 글 목록`,
  }
}

export default async function CategoryPage({ params, searchParams }: PageProps) {
  const { slug } = await params
  const { page: pageParam } = await searchParams
  const currentPage = Number(pageParam) || 1

  const [category, categories] = await Promise.all([
    getCategoryBySlug(slug),
    getCategories(),
  ])

  if (!category) notFound()

  const { posts, totalPages } = await getPosts({
    category: category.id,
    page: currentPage,
    perPage: 9,
  })

  return (
    <main>
      <div className="container mx-auto px-5 max-w-6xl">
        <Intro />
        <CategoryNav categories={categories} activeSlug={slug} />

        <div className="mb-10">
          <h2 className="text-2xl md:text-3xl font-black tracking-tight">
            {category.name}
          </h2>
          {category.description && (
            <p className="text-muted-foreground text-sm mt-1">{category.description}</p>
          )}
        </div>

        {posts.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-10 mb-16">
            {posts.map((post) => (
              <PostPreview key={post.id} post={post} />
            ))}
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-20 text-lg">
            이 카테고리에 아직 글이 없습니다.
          </p>
        )}

        <Pagination currentPage={currentPage} totalPages={totalPages} basePath={`/category/${slug}`} />
      </div>
    </main>
  )
}
