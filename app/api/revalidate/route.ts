import { revalidatePath } from "next/cache"
import { NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  const secret = request.headers.get("x-revalidation-secret")

  if (secret !== process.env.REVALIDATION_SECRET) {
    return NextResponse.json({ message: "Invalid secret" }, { status: 401 })
  }

  try {
    const body = await request.json()
    const slug = body?.post?.post_name || body?.slug

    // Revalidate home page
    revalidatePath("/")

    // Revalidate specific post page if slug provided
    if (slug) {
      revalidatePath(`/posts/${slug}`)
    }

    // Revalidate category and tag pages
    revalidatePath("/category/[slug]", "page")
    revalidatePath("/tag/[slug]", "page")

    return NextResponse.json({
      revalidated: true,
      slug: slug || null,
      now: Date.now(),
    })
  } catch {
    return NextResponse.json(
      { message: "Error revalidating" },
      { status: 500 }
    )
  }
}
