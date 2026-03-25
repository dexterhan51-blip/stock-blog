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
      <h2 className="text-xl font-extrabold tracking-tight mb-6">
        {title}
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-5 gap-y-10">
        {posts.map((post) => (
          <PostPreview key={post.id} post={post} />
        ))}
      </div>
    </section>
  )
}
