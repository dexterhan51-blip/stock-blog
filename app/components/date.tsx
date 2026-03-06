import { format } from "date-fns"
import { ko } from "date-fns/locale"

export default function DateComponent({ dateString }: { dateString: string }) {
  return (
    <time dateTime={dateString}>
      {format(new Date(dateString), "yyyy년 M월 d일", { locale: ko })}
    </time>
  )
}
