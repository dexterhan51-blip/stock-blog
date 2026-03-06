import Link from "next/link"
import type { Metadata } from "next"
import { notFound } from "next/navigation"
import { getPostBySlug, getPosts, getAllPostSlugs } from "@/lib/queries"
import { PostBody } from "@/app/components/post-body"
import { MoreStories } from "@/app/components/more-stories"
import CoverImage from "@/app/components/cover-image"
import Date from "@/app/components/date"
import { Badge } from "@/components/ui/badge"
import { BLOG_NAME, SITE_URL } from "@/lib/constants"
import { ArrowLeft, BarChart3 } from "lucide-react"

export const revalidate = 300

export async function generateStaticParams() {
  const slugs = await getAllPostSlugs()
  return slugs.map((slug) => ({ slug }))
}

type PageProps = { params: Promise<{ slug: string }> }

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { slug } = await params
  const post = await getPostBySlug(slug)
  if (!post) return {}

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      url: `${SITE_URL}/posts/${post.slug}`,
      siteName: BLOG_NAME,
      type: "article",
      publishedTime: post.date,
      modifiedTime: post.modified,
      images: post.coverImage
        ? [{ url: post.coverImage.url, width: post.coverImage.width, height: post.coverImage.height, alt: post.title }]
        : [],
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description: post.excerpt,
      images: post.coverImage ? [post.coverImage.url] : [],
    },
  }
}

export default async function PostPage({ params }: PageProps) {
  const { slug } = await params
  const post = await getPostBySlug(slug)
  if (!post) notFound()

  const { posts: relatedPosts } = await getPosts({ perPage: 4 })
  const morePosts = relatedPosts.filter((p) => p.slug !== slug).slice(0, 3)

  return (
    <main>
      <div className="container mx-auto px-5 max-w-6xl">
        {/* Compact header */}
        <div className="flex items-center justify-between py-4 border-b border-border mb-8">
          <Link href="/" className="group inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
            <ArrowLeft className="w-3.5 h-3.5" />
            <BarChart3 className="w-3.5 h-3.5 text-primary" />
            <span className="font-bold">{BLOG_NAME}</span>
          </Link>
        </div>

        <article className="max-w-3xl mx-auto">
          {/* Category label */}
          {post.categories.length > 0 && (
            <div className="mb-4">
              <Link href={`/category/${post.categories[0].slug}`}>
                <span className="text-xs font-bold text-accent uppercase tracking-wider hover:text-accent/80 transition-colors">
                  {post.categories[0].name}
                </span>
              </Link>
            </div>
          )}

          {/* Title */}
          <h1 className="text-3xl md:text-4xl lg:text-[2.75rem] font-black leading-[1.15] tracking-tight mb-5">
            {post.title}
          </h1>

          {/* Meta */}
          <div className="flex items-center gap-3 text-sm text-muted-foreground mb-8 pb-6 border-b">
            {post.author && <span className="font-medium text-foreground">{post.author.name}</span>}
            {post.author && <span className="text-border">|</span>}
            <Date dateString={post.date} />
          </div>

          {/* Cover */}
          {post.coverImage && (
            <div className="mb-10 rounded-lg overflow-hidden">
              <CoverImage
                title={post.title}
                url={post.coverImage.url}
                width={1200}
                height={675}
                priority
                className="rounded-lg"
              />
            </div>
          )}

          {/* Tags */}
          {post.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-8">
              {post.tags.map((tag) => (
                <Link key={tag.id} href={`/tag/${tag.slug}`}>
                  <Badge variant="outline" className="cursor-pointer text-xs">
                    #{tag.name}
                  </Badge>
                </Link>
              ))}
            </div>
          )}

          {/* Body */}
          <PostBody content={post.content} />
        </article>

        {morePosts.length > 0 && (
          <div className="mt-20 pt-10 border-t">
            <MoreStories posts={morePosts} title="More Stories" />
          </div>
        )}
      </div>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Article",
            headline: post.title,
            description: post.excerpt,
            datePublished: post.date,
            dateModified: post.modified,
            author: post.author ? { "@type": "Person", name: post.author.name } : undefined,
            image: post.coverImage?.url,
            publisher: { "@type": "Organization", name: BLOG_NAME },
          }),
        }}
      />
    </main>
  )
}
