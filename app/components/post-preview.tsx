import Link from "next/link"
import Date from "./date"
import CoverImage from "./cover-image"
import type { Post } from "@/lib/types"

export function PostPreview({ post }: { post: Post }) {
  return (
    <article className="group">
      <Link href={`/posts/${post.slug}`} className="block">
        {/* Image */}
        <div className="aspect-[16/10] overflow-hidden rounded-lg mb-3">
          {post.coverImage ? (
            <CoverImage
              title={post.title}
              url={post.coverImage.url}
              width={700}
              height={438}
              className="rounded-lg group-hover:scale-[1.03] transition-transform duration-500"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-primary/8 via-muted to-accent/8 flex items-center justify-center rounded-lg">
              <span className="text-3xl font-black text-primary/15 select-none">
                {post.categories[0]?.name?.[0] || "M"}
              </span>
            </div>
          )}
        </div>

        {/* Content */}
        <div>
          {post.categories.length > 0 && (
            <span className="text-xs font-bold text-accent uppercase tracking-wider">
              {post.categories[0].name}
            </span>
          )}
          <h3 className="text-base md:text-lg font-bold leading-snug mt-1 mb-1.5 group-hover:text-primary transition-colors line-clamp-2">
            {post.title}
          </h3>
          <p className="text-muted-foreground text-sm leading-relaxed line-clamp-2 mb-2">
            {post.excerpt}
          </p>
          <span className="text-xs text-muted-foreground">
            <Date dateString={post.date} />
          </span>
        </div>
      </Link>
    </article>
  )
}
