#!/usr/bin/env python3
"""미장웃장 블로그 글 리라이팅 — 한대디/아들 컨셉 → 미장웃장 컨셉 변환"""

import json
import re
import urllib.request
import urllib.error
import base64
import time
import sys

WP_API = "https://wordpress-1592891-6259767.cloudwaysapps.com/wp-json/wp/v2"
WP_AUTH = base64.b64encode(b"dexterhan51@gmail.com:pkOC VTKe 9VuM rhLn 4yuz UGPK").decode()

# ============================================================
# 리라이팅 함수
# ============================================================

def rewrite_content(html: str, title: str) -> str:
    """한대디/아들 컨셉을 미장웃장 컨셉으로 변환"""

    # 1) Q&A 블록 처리: <p><strong>Q: ...</strong></p> + <p><strong>A: ...</strong></p>
    #    Q는 제거, A의 내용만 일반 문단으로 변환
    def replace_qa_block(match):
        a_text = match.group(1).strip()
        if not a_text:
            return ""
        # "~야.", "~지.", "~거야" 등 반말 → "~에요.", "~거든요." 변환
        a_text = convert_to_polite(a_text)
        return f"<p>{a_text}</p>"

    # Q&A 패턴: Q줄 + A줄 (연속)
    html = re.sub(
        r'<p>\s*<strong>\s*Q\s*[:：]\s*.*?</strong>\s*</p>\s*'
        r'<p>\s*<strong>\s*A\s*[:：]\s*(.*?)</strong>\s*</p>',
        replace_qa_block, html, flags=re.DOTALL
    )

    # 남은 단독 Q 라인 제거
    html = re.sub(
        r'<p>\s*<strong>\s*Q\s*[:：]\s*.*?</strong>\s*</p>',
        '', html
    )
    # 남은 단독 A 라인 → 일반 문단
    def replace_lone_a(match):
        text = match.group(1).strip()
        if not text:
            return ""
        text = convert_to_polite(text)
        return f"<p>{text}</p>"
    html = re.sub(
        r'<p>\s*<strong>\s*A\s*[:：]\s*(.*?)</strong>\s*</p>',
        replace_lone_a, html
    )

    # 2) 한대디 인트로 패턴 제거
    intro_patterns = [
        r'<p>안녕하세요[,，]?\s*아들\s*눈높이[로에서]*\s*미국\s*주식[을를]?\s*쉽게\s*풀어\s*설명하는\s*한대디입니다\.?\s*</p>',
        r'<p>안녕하세요[,，]?\s*아들\s*눈높이[로에서]*\s*미국\s*주식\s*설명하는\s*한대디입니다\.?\s*</p>',
        r'<p>안녕하세요[,，]?\s*.*?한대디입니다\.?\s*</p>',
    ]
    for pat in intro_patterns:
        html = re.sub(pat, '', html, flags=re.IGNORECASE)

    # 3) "한대디" 텍스트 변환 — "한대디의 아들 추천 지수" 섹션 전체 제거
    # HTML 엔티티 포함 패턴: &#8211; = –, &#8216; = ', &#8217; = '
    html = re.sub(r'<p>\s*한대디의\s*아들\s*추천\s*지수.*?</p>', '', html, flags=re.DOTALL)
    html = re.sub(r'한대디의\s*추천지수.*?(?=<h2|<hr|$)', '', html, flags=re.DOTALL)
    html = re.sub(r'한대디의\s*R-index.*?(?=<h2|<hr|$)', '', html, flags=re.DOTALL)
    # "한대디의 아들 추천 지수 – R index" 포함 h2/h3 제거
    html = re.sub(r'<h[23]>.*?한대디.*?추천.*?지수.*?</h[23]>', '', html, flags=re.DOTALL)
    html = html.replace('한대디', '저')
    html = html.replace('한 대디', '저')

    # 4) "아들" 관련 표현 제거/변환
    # "아들이 'xxx'를 쉽게 이해할 수 있게/있도록 포스팅해 보겠습니다" 패턴
    html = re.sub(r'<p>\s*아들이\s*.*?쉽게\s*이해.*?</p>', '', html, flags=re.DOTALL)
    # "오늘은 아들이 'xxx'를 쉽게 이해할 수 있도록 정리해 보겠습니다." — 문장 중간에 있는 경우
    html = re.sub(r'아들이\s*.*?쉽게\s*이해할\s*수\s*있[게도]록?\s*.*?(?=</p>)', '', html)
    html = re.sub(r'아들\s*눈높이[로에서]*', '', html)
    # "아들이 &#8216;슈드&#8217;를" 패턴 (HTML 엔티티 포함)
    html = re.sub(r'아들이\s*&#8216;.*?&#8217;[를을]?\s*', '', html)
    html = re.sub(r'아빠가\s*', '', html)
    html = re.sub(r'아빠랑\s*', '', html)
    html = re.sub(r'아들\s*', '', html)  # 최종 안전망

    # 5) 이모지 제거
    html = re.sub(r'📍\s*', '', html)
    html = re.sub(r'🔍\s*', '', html)
    html = re.sub(r'💡\s*', '', html)
    html = re.sub(r'📊\s*', '', html)
    html = re.sub(r'✅\s*', '', html)
    html = re.sub(r'🔥\s*', '', html)

    # 6) "오늘 살펴볼 내용" 목차 블록 → 간단한 h2로 대체하거나 제거
    # 보통 <p>오늘 살펴볼 내용</p> 다음에 <p> 리스트가 이어짐
    html = re.sub(r'<p>\s*오늘\s*살펴볼\s*내용\s*</p>', '', html)

    # 7) 마무리 패턴 교체
    outro_patterns = [
        r'<p>.*?댓글로\s*질문\s*주시면.*?</p>',
        r'<p>.*?여러분들의\s*성공적인\s*투자를\s*진심으로\s*응원합니다[!！]*\s*</p>',
        r'<p>.*?헷갈리시는\s*분은.*?</p>',
    ]
    for pat in outro_patterns:
        html = re.sub(pat, '', html)

    # 마지막에 표준 아웃트로가 없으면 추가
    standard_outro = '<p>투자 판단은 각자의 몫이에요. 같이 공부하는 마음으로 봐주세요.</p>'
    if '투자 판단은 각자의 몫' not in html:
        # 마지막 </p> 뒤에 추가
        html = html.rstrip()
        if html.endswith('</p>'):
            html += '\n' + standard_outro
        else:
            html += '\n' + standard_outro

    # 8) 빈 줄 / 빈 <p></p> 정리
    html = re.sub(r'<p>\s*</p>', '', html)
    html = re.sub(r'\n{3,}', '\n\n', html)
    html = html.strip()

    return html


def rewrite_title(title: str) -> str:
    """제목에서 한대디/아들 관련 텍스트 제거"""
    title = title.replace('한대디의 ', '').replace('한대디 ', '')
    title = re.sub(r'^아들아[!！]?\s*', '', title)
    # 특수 케이스
    if '한대디' in title:
        title = title.replace('한대디', '').strip()
    return title.strip()


def convert_to_polite(text: str) -> str:
    """반말을 존댓말로 변환 (간단한 패턴)"""
    # ~야. → ~에요.
    text = re.sub(r'([가-힣])야\.', r'\1예요.', text)
    text = re.sub(r'([가-힣])야$', r'\1예요', text)
    # ~지. → ~죠.
    text = re.sub(r'([가-힣])지\.', r'\1죠.', text)
    # ~거야 → ~거예요
    text = re.sub(r'거야\.?', '거예요.', text)
    # ~이야 → ~이에요
    text = re.sub(r'이야\.?', '이에요.', text)
    # ~는데... → ~는데요...
    # ~거든 → ~거든요
    text = re.sub(r'거든([^요])', r'거든요\1', text)
    text = re.sub(r'거든$', '거든요', text)
    return text


def rewrite_post_60(html: str) -> str:
    """ID 60 특별 처리: 한대디 근황 → 블로그 소개"""
    return """<p>퇴근 후에 시작되는 투자 이야기를 기록하는 블로그를 시작합니다.</p>
<p>직장인으로서 미국 주식을 공부하면서 느낀 점, 분석한 내용, 실수했던 경험까지 솔직하게 남겨보려고 해요.</p>
<hr/>
<h2>이 블로그에서 다루는 내용</h2>
<ul>
<li><strong>개별 종목 분석</strong>: 미국 주식 실적 분석과 투자 포인트 정리</li>
<li><strong>ETF 투자</strong>: SCHD, QQQ, 커버드콜 등 다양한 ETF 비교</li>
<li><strong>경제 이슈</strong>: CPI, 환율, 관세 등 시장에 영향을 주는 이슈 정리</li>
<li><strong>투자 경험</strong>: 수익 인증, 실패 경험, 포트폴리오 공유</li>
</ul>
<p>전문가가 아니라 같이 공부하는 사람이에요. 틀린 내용이 있으면 편하게 알려주세요.</p>
<p>투자 판단은 각자의 몫이에요. 같이 공부하는 마음으로 봐주세요.</p>"""


# ============================================================
# WordPress API 함수
# ============================================================

def wp_update_post(post_id: int, title: str, content: str) -> dict:
    """WordPress REST API로 글 업데이트"""
    url = f"{WP_API}/posts/{post_id}"
    payload = json.dumps({"title": title, "content": content}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="PUT")
    req.add_header("Authorization", f"Basic {WP_AUTH}")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"error": True, "status": e.code, "body": body[:500]}


# ============================================================
# 메인
# ============================================================

def main():
    # 저장된 포스트 로드
    with open("/Users/dexterhan/Documents/Projects/side-projects/econ-blog/scripts/posts-to-rewrite.json") as f:
        posts = json.load(f)

    results = []
    dry_run = "--dry-run" in sys.argv

    for post in posts:
        pid = post["id"]
        old_title = post["title"]["rendered"]
        old_content = post["content"]["rendered"]

        # 특수 케이스: ID 60
        if pid == 60:
            new_title = "블로그를 시작하며 — 퇴근 후 투자 이야기"
            new_content = rewrite_post_60(old_content)
        else:
            new_title = rewrite_title(old_title)
            new_content = rewrite_content(old_content, new_title)

        if dry_run:
            print(f"\n{'='*60}")
            print(f"POST {pid}: {old_title}")
            print(f"  → NEW TITLE: {new_title}")
            print(f"  → CONTENT PREVIEW (first 300 chars):")
            print(f"    {new_content[:300]}")
            # Check for remaining issues
            issues = []
            if '한대디' in new_content: issues.append('한대디 남음')
            if '아들' in new_content and '아들러' not in new_content: issues.append('아들 남음')
            if '<strong>Q:' in new_content or '<strong>A:' in new_content: issues.append('Q&A 남음')
            if issues:
                print(f"  ⚠️ ISSUES: {', '.join(issues)}")
            else:
                print(f"  ✓ CLEAN")
            results.append({"id": pid, "title": new_title, "issues": issues})
        else:
            result = wp_update_post(pid, new_title, new_content)
            status = "ERROR" if "error" in result else "OK"
            print(f"[{status}] Post {pid}: {new_title}")
            if status == "ERROR":
                print(f"  Error: {result}")
            results.append({"id": pid, "title": new_title, "status": status})
            time.sleep(0.5)  # Rate limiting

    # 결과 저장
    out_file = "/Users/dexterhan/Documents/Projects/side-projects/econ-blog/scripts/rewrite-results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to {out_file}")


if __name__ == "__main__":
    main()
