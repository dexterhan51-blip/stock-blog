import Link from "next/link"
import Date from "./date"
import CoverImage from "./cover-image"
import type { Post } from "@/lib/types"
import { ArrowRight } from "lucide-react"

export function HeroPost({ post }: { post: Post }) {
  return (
    <section className="mb-12">
      <Link href={`/posts/${post.slug}`} className="group block">
        <div className="grid md:grid-cols-5 gap-0 bg-card rounded-lg overflow-hidden border border-border hover:border-primary/30 transition-colors">
          {/* Image: 3 cols */}
          <div className="md:col-span-3 relative aspect-[16/9] md:aspect-auto overflow-hidden">
            {post.coverImage ? (
              <CoverImage
                title={post.title}
                url={post.coverImage.url}
                width={900}
                height={506}
                className="h-full rounded-none group-hover:scale-[1.02] transition-transform duration-700"
                priority
              />
            ) : (
              <div className="h-full min-h-[280px] bg-gradient-to-br from-primary/10 via-muted to-accent/10 flex items-center justify-center">
                <span className="text-6xl font-black text-primary/15 select-none">
                  {post.categories[0]?.name?.[0] || "M"}
                </span>
              </div>
            )}
          </div>

          {/* Content: 2 cols */}
          <div className="md:col-span-2 p-6 md:p-8 flex flex-col justify-center">
            {post.categories.length > 0 && (
              <span className="text-xs font-bold text-accent uppercase tracking-wider mb-3">
                {post.categories[0].name}
              </span>
            )}
            <h2 className="text-xl md:text-2xl lg:text-3xl font-black leading-tight mb-3 group-hover:text-primary transition-colors">
              {post.title}
            </h2>
            <p className="text-muted-foreground text-sm leading-relaxed mb-5 line-clamp-3">
              {post.excerpt}
            </p>
            <div className="flex items-center justify-between mt-auto">
              <span className="text-xs text-muted-foreground">
                <Date dateString={post.date} />
              </span>
              <span className="inline-flex items-center gap-1 text-sm font-semibold text-primary group-hover:gap-2 transition-all">
                Read
                <ArrowRight className="w-3.5 h-3.5" />
              </span>
            </div>
          </div>
        </div>
      </Link>
    </section>
  )
}
