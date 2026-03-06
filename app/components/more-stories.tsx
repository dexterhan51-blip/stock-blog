import { PostPreview } from "./post-preview"
import type { Post } from "@/lib/types"

export function MoreStories({
  posts,
  title,
}: {
  posts: Post[]
  title: string
}) {
  return (
    <section className="mb-16">
      <div className="flex items-center gap-3 mb-6">
        <h2 className="text-lg font-black tracking-tight uppercase">
          {title}
        </h2>
        <div className="flex-1 h-px bg-border" />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-10">
        {posts.map((post) => (
          <PostPreview key={post.id} post={post} />
        ))}
      </div>
    </section>
  )
}
