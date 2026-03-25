import Link from "next/link"
import Date from "./date"
import CoverImage from "./cover-image"
import type { Post } from "@/lib/types"

export function PostPreview({ post }: { post: Post }) {
  return (
    <article className="group">
      <Link href={`/posts/${post.slug}`} className="block bg-card rounded-2xl overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5">
        {/* Image */}
        <div className="aspect-[16/9] overflow-hidden">
          {post.coverImage ? (
            <CoverImage
              title={post.title}
              url={post.coverImage.url}
              width={700}
              height={394}
              className="rounded-none group-hover:scale-[1.03] transition-transform duration-500"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-primary/8 via-muted to-accent/8 flex items-center justify-center">
              <span className="text-3xl font-black text-primary/15 select-none">
                {post.categories[0]?.name?.[0] || "M"}
              </span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-4 pb-5">
          {post.categories.length > 0 && (
            <span className="inline-block text-xs font-semibold text-muted-foreground bg-muted px-2.5 py-0.5 rounded-md mb-2">
              {post.categories[0].name}
            </span>
          )}
          <h3 className="text-base md:text-lg font-bold leading-snug mb-1.5 group-hover:text-primary transition-colors line-clamp-2">
            {post.title}
          </h3>
          <p className="text-muted-foreground text-sm leading-relaxed line-clamp-2 mb-3">
            {post.excerpt}
          </p>
          <span className="text-xs text-muted-foreground/70">
            <Date dateString={post.date} />
          </span>
        </div>
      </Link>
    </article>
  )
}
