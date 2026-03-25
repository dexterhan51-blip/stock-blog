import Link from "next/link"
import Date from "./date"
import CoverImage from "./cover-image"
import type { Post } from "@/lib/types"

export function HeroPost({ post }: { post: Post }) {
  return (
    <section className="py-8 mb-2">
      <Link href={`/posts/${post.slug}`} className="group block">
        <div className="flex flex-col lg:flex-row-reverse gap-6 lg:gap-10 items-center">
          {/* Image — right on desktop */}
          <div className="w-full lg:w-3/5 aspect-[16/9] overflow-hidden rounded-2xl">
            {post.coverImage ? (
              <CoverImage
                title={post.title}
                url={post.coverImage.url}
                width={900}
                height={506}
                className="rounded-2xl group-hover:scale-[1.02] transition-transform duration-700"
                priority
              />
            ) : (
              <div className="w-full h-full bg-gradient-to-br from-primary/10 via-muted to-accent/10 flex items-center justify-center rounded-2xl">
                <span className="text-6xl font-black text-primary/15 select-none">
                  {post.categories[0]?.name?.[0] || "M"}
                </span>
              </div>
            )}
          </div>

          {/* Content — left on desktop */}
          <div className="w-full lg:w-2/5 flex flex-col justify-center">
            <h2 className="text-2xl md:text-3xl lg:text-[32px] font-extrabold leading-tight mb-3 group-hover:text-primary transition-colors line-clamp-2">
              {post.title}
            </h2>
            <p className="text-muted-foreground text-[15px] leading-relaxed mb-4 line-clamp-3">
              {post.excerpt}
            </p>
            <div className="flex flex-wrap gap-1.5 mb-4">
              {post.categories.map((cat) => (
                <span
                  key={cat.id}
                  className="text-xs font-semibold text-muted-foreground bg-muted px-2.5 py-1 rounded-full"
                >
                  {cat.name}
                </span>
              ))}
            </div>
            <span className="text-xs text-muted-foreground/70">
              <Date dateString={post.date} />
            </span>
          </div>
        </div>
      </Link>
    </section>
  )
}
