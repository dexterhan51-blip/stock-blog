import { fetchAPI, getTotalPages } from "./wordpress"
import { normalizePost, type Post, type Category, type Tag, type WPPost, type WPCategory, type WPTag } from "./types"

interface GetPostsParams {
  page?: number
  perPage?: number
  category?: number
  tag?: number
  search?: string
}

interface GetPostsResult {
  posts: Post[]
  totalPages: number
}

export async function getPosts(
  params?: GetPostsParams,
  revalidate = 60
): Promise<GetPostsResult> {
  const queryParams: Record<string, string> = {
    _embed: "true",
    orderby: "date",
    order: "desc",
    per_page: String(params?.perPage || 10),
    page: String(params?.page || 1),
  }

  if (params?.category) queryParams.categories = String(params.category)
  if (params?.tag) queryParams.tags = String(params.tag)
  if (params?.search) queryParams.search = params.search

  const data = await fetchAPI<WPPost[]>("/posts", queryParams, revalidate)
  return {
    posts: data.map(normalizePost),
    totalPages: getTotalPages(data),
  }
}

export async function getPostBySlug(slug: string, revalidate = 300): Promise<Post | null> {
  const data = await fetchAPI<WPPost[]>(
    "/posts",
    { slug, _embed: "true" },
    revalidate
  )
  return data.length > 0 ? normalizePost(data[0]) : null
}

export async function getAllPostSlugs(): Promise<string[]> {
  const slugs: string[] = []
  let page = 1
  let hasMore = true

  while (hasMore) {
    const data = await fetchAPI<WPPost[]>("/posts", {
      per_page: "100",
      page: String(page),
      _fields: "slug",
    })
    slugs.push(...data.map((p) => p.slug))
    hasMore = data.length === 100
    page++
  }

  return slugs
}

export async function getCategories(revalidate = 120): Promise<Category[]> {
  const data = await fetchAPI<WPCategory[]>(
    "/categories",
    { per_page: "100", hide_empty: "true" },
    revalidate
  )
  return data.map((c) => ({
    id: c.id,
    name: c.name,
    slug: c.slug,
    count: c.count,
    description: c.description || "",
  }))
}

export async function getCategoryBySlug(slug: string, revalidate = 120): Promise<Category | null> {
  const data = await fetchAPI<WPCategory[]>(
    "/categories",
    { slug },
    revalidate
  )
  if (data.length === 0) return null
  const c = data[0]
  return {
    id: c.id,
    name: c.name,
    slug: c.slug,
    count: c.count,
    description: c.description || "",
  }
}

export async function getTags(revalidate = 120): Promise<Tag[]> {
  const data = await fetchAPI<WPTag[]>(
    "/tags",
    { per_page: "100", hide_empty: "true" },
    revalidate
  )
  return data.map((t) => ({
    id: t.id,
    name: t.name,
    slug: t.slug,
    count: t.count,
  }))
}

export async function getTagBySlug(slug: string, revalidate = 120): Promise<Tag | null> {
  const data = await fetchAPI<WPTag[]>(
    "/tags",
    { slug },
    revalidate
  )
  if (data.length === 0) return null
  const t = data[0]
  return {
    id: t.id,
    name: t.name,
    slug: t.slug,
    count: t.count,
  }
}
