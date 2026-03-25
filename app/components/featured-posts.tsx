import { PostPreview } from "./post-preview"
import type { Post } from "@/lib/types"

export function FeaturedPosts({ posts }: { posts: Post[] }) {
  return (
    <section className="mb-12">
      <h2 className="text-xl font-extrabold tracking-tight mb-5">
        추천 글
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-x-5 gap-y-8">
        {posts.map((post) => (
          <PostPreview key={post.id} post={post} />
        ))}
      </div>
    </section>
  )
}
