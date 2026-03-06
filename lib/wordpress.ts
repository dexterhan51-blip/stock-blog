const WP_API_URL = process.env.WORDPRESS_API_URL

export async function fetchAPI<T>(
  endpoint: string,
  params?: Record<string, string>,
  revalidate = 60
): Promise<T> {
  if (!WP_API_URL) {
    // Return empty array or object when no API URL configured
    return [] as unknown as T
  }

  const url = new URL(`${WP_API_URL}${endpoint}`)
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.set(key, value)
    })
  }

  const res = await fetch(url.toString(), {
    next: { revalidate },
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!res.ok) {
    throw new Error(`WordPress API error: ${res.status} ${res.statusText}`)
  }

  const data = await res.json()
  const totalPages = res.headers.get("X-WP-TotalPages")

  // Attach totalPages to the response for pagination
  if (Array.isArray(data)) {
    ;(data as T & { _totalPages?: number })._totalPages = totalPages
      ? parseInt(totalPages, 10)
      : 1
  }

  return data as T
}

// Helper to get total pages from a fetched array
export function getTotalPages<T>(data: T[]): number {
  return (data as T[] & { _totalPages?: number })._totalPages || 1
}
