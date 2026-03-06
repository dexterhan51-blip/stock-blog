// WordPress REST API raw types
export interface WPPost {
  id: number
  slug: string
  title: { rendered: string }
  content: { rendered: string }
  excerpt: { rendered: string }
  date: string
  modified: string
  featured_media: number
  categories: number[]
  tags: number[]
  _embedded?: {
    author?: WPAuthor[]
    "wp:featuredmedia"?: WPMedia[]
    "wp:term"?: [WPCategory[], WPTag[]]
  }
}

export interface WPCategory {
  id: number
  name: string
  slug: string
  count: number
  description: string
}

export interface WPTag {
  id: number
  name: string
  slug: string
  count: number
}

export interface WPAuthor {
  id: number
  name: string
  avatar_urls: Record<string, string>
}

export interface WPMedia {
  id: number
  source_url: string
  alt_text: string
  media_details?: {
    width: number
    height: number
  }
}

// Normalized types for components
export interface Post {
  id: number
  slug: string
  title: string
  content: string
  excerpt: string
  date: string
  modified: string
  coverImage: {
    url: string
    alt: string
    width: number
    height: number
  } | null
  author: {
    name: string
    avatarUrl: string
  } | null
  categories: Category[]
  tags: Tag[]
}

export interface Category {
  id: number
  name: string
  slug: string
  count: number
  description: string
}

export interface Tag {
  id: number
  name: string
  slug: string
  count: number
}

// Normalize WP data to component-friendly format
export function normalizePost(raw: WPPost): Post {
  const media = raw._embedded?.["wp:featuredmedia"]?.[0]
  const author = raw._embedded?.author?.[0]
  const terms = raw._embedded?.["wp:term"]

  return {
    id: raw.id,
    slug: raw.slug,
    title: raw.title.rendered,
    content: raw.content.rendered,
    excerpt: raw.excerpt.rendered.replace(/<[^>]+>/g, "").trim(),
    date: raw.date,
    modified: raw.modified,
    coverImage: media
      ? {
          url: media.source_url,
          alt: media.alt_text || raw.title.rendered,
          width: media.media_details?.width || 1200,
          height: media.media_details?.height || 630,
        }
      : null,
    author: author
      ? {
          name: author.name,
          avatarUrl: author.avatar_urls?.["96"] || author.avatar_urls?.["48"] || "",
        }
      : null,
    categories: terms?.[0]?.map((c) => ({
      id: c.id,
      name: c.name,
      slug: c.slug,
      count: c.count,
      description: c.description || "",
    })) || [],
    tags: terms?.[1]?.map((t) => ({
      id: t.id,
      name: t.name,
      slug: t.slug,
      count: t.count,
    })) || [],
  }
}
