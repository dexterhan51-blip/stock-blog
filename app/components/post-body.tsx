import parse from "html-react-parser"
import sanitizeHtml from "sanitize-html"

export function PostBody({ content }: { content: string }) {
  const clean = sanitizeHtml(content, {
    allowedTags: sanitizeHtml.defaults.allowedTags.concat([
      "img",
      "figure",
      "figcaption",
      "iframe",
      "video",
      "source",
    ]),
    allowedAttributes: {
      ...sanitizeHtml.defaults.allowedAttributes,
      img: ["src", "alt", "width", "height", "loading", "class"],
      iframe: ["src", "width", "height", "frameborder", "allow", "allowfullscreen"],
      video: ["src", "controls", "width", "height"],
      source: ["src", "type"],
      a: ["href", "target", "rel"],
      "*": ["class", "id"],
    },
    allowedIframeHostnames: ["www.youtube.com", "youtube.com", "player.vimeo.com"],
  })

  return (
    <div className="prose dark:prose-invert prose-lg max-w-2xl mx-auto prose-a:text-primary hover:prose-a:text-primary/80 prose-img:rounded-lg">
      {parse(clean)}
    </div>
  )
}
