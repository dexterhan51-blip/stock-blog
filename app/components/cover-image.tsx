import Link from "next/link"
import Image from "next/image"
import { cn } from "@/lib/utils"

export default function CoverImage({
  title,
  url,
  slug,
  width,
  height,
  priority,
  className,
}: {
  title: string
  url: string
  slug?: string
  width: number
  height: number
  priority?: boolean
  className?: string
}) {
  const image = (
    <Image
      alt={`Cover Image for ${title}`}
      width={width}
      height={height}
      priority={priority}
      className={cn("object-cover w-full", className, {
        "transition-all duration-300": slug,
      })}
      src={url}
    />
  )

  return slug ? (
    <Link href={`/posts/${slug}`} aria-label={title}>
      {image}
    </Link>
  ) : (
    image
  )
}
