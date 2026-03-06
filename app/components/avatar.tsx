import Image from "next/image"

export default function Avatar({ name, url }: { name: string; url: string }) {
  return (
    <div className="flex items-center">
      <div className="mr-4 w-12 h-12 relative">
        <Image
          alt={name}
          className="object-cover rounded-full"
          fill
          sizes="48px"
          src={url}
        />
      </div>
      <div className="text-xl font-bold">{name}</div>
    </div>
  )
}
