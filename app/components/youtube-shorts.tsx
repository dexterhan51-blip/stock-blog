"use client"

const SHORTS = [
  { id: "37vtvpk_h9w", title: "삼성전자 vs SK하이닉스 주식에 1천만 원 투자했다면?" },
  { id: "TCdPmw6fa80", title: "팔란티어 2배 레버리지 주식에 1만 달러 투자했다면?" },
  { id: "WUhabXldqPY", title: "네이버 주식에 천 만원 투자했다면?" },
  { id: "Ny8Sz_t60gg", title: "한화 에어로스페이스 주식에 천 만원 투자했다면?" },
  { id: "bD6d8D__f2w", title: "애플 vs 삼성전자 주식에 $10,000 투자했다면?" },
  { id: "_AB7xg_uc_I", title: "QQQ VS SPY ETF에 $10,000 투자 했다면?" },
  { id: "wkNGCFkk_Os", title: "게임스탑에 $10,000 투자했다면?" },
  { id: "QfTkbl9qibo", title: "비트코인 VS 엔비디아 주식에 $10,000 투자 했다면?" },
]

export function YoutubeShorts() {
  return (
    <section className="mb-12">
      <h2 className="text-xl font-extrabold tracking-tight mb-5">
        클립 영상
      </h2>
      <div className="flex gap-3.5 overflow-x-auto pb-3 scrollbar-hide">
        {SHORTS.map((short) => (
          <div key={short.id} className="flex-shrink-0 w-[160px] sm:w-[180px]">
            <iframe
              src={`https://www.youtube.com/embed/${short.id}`}
              className="w-full aspect-[9/16] rounded-xl border-0 bg-muted"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              loading="lazy"
            />
            <p className="text-xs font-medium text-muted-foreground mt-2 line-clamp-2 leading-snug">
              {short.title}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}
