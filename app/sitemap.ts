import type { MetadataRoute } from "next"
import { getAllPostSlugs, getCategories } from "@/lib/queries"
import { SITE_URL } from "@/lib/constants"

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [slugs, categories] = await Promise.all([
    getAllPostSlugs(),
    getCategories(),
  ])

  const postEntries: MetadataRoute.Sitemap = slugs.map((slug) => ({
    url: `${SITE_URL}/posts/${slug}`,
    changeFrequency: "weekly",
    priority: 0.8,
  }))

  const categoryEntries: MetadataRoute.Sitemap = categories.map((cat) => ({
    url: `${SITE_URL}/category/${cat.slug}`,
    changeFrequency: "weekly",
    priority: 0.6,
  }))

  return [
    {
      url: SITE_URL,
      changeFrequency: "daily",
      priority: 1,
    },
    ...postEntries,
    ...categoryEntries,
  ]
}
