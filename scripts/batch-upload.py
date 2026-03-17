#!/usr/bin/env python3
"""네이버 블로그 크롤링 원고를 WordPress에 예약발행 + Recraft 대표이미지 생성"""

import json
import urllib.request
import urllib.error
import base64
import time
import os
import re
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

# === CONFIG ===
RECRAFT_API_KEY = "AB96m9eEZ17sJxnjrVUoGVF3ZWlOXgjuyz6N4oWckeS22peD4bDjnINirB8JlnaC"
RECRAFT_URL = "https://external.api.recraft.ai/v1/images/generations"

WP_API = "https://wordpress-1592891-6259767.cloudwaysapps.com/wp-json/wp/v2"
WP_USER = "dexterhan51@gmail.com"
WP_APP_PASSWORD = "pkOC VTKe 9VuM rhLn 4yuz UGPK"

ARTICLES_DIR = Path("/Users/dexterhan/Documents/Projects/tools/naver-blog-crawler/output/articles")

# 3 posts per day: morning, lunch, evening (KST, WordPress uses this timezone)
SCHEDULE_TIMES = ["08:00:00", "12:30:00", "18:00:00"]
START_DATE = "2026-03-08"  # First scheduled date

# Category mapping
CATEGORIES = {
    "stocks": 2,
    "real-estate": 3,
    "economic-policy": 4,
    "investment": 5,
    "global-economy": 6,
    "daily-economy": 7,
    "crypto": 8,
}

# Keyword -> category mapping
KEYWORD_CATEGORIES = {
    "엔비디아": ["stocks"],
    "NVDA": ["stocks"],
    "팔란티어": ["stocks"],
    "PLTR": ["stocks"],
    "테슬라": ["stocks"],
    "TSLA": ["stocks"],
    "애플": ["stocks"],
    "AAPL": ["stocks"],
    "마이크로소프트": ["stocks"],
    "MSFT": ["stocks"],
    "구글": ["stocks"],
    "알파벳": ["stocks"],
    "아마존": ["stocks"],
    "AMZN": ["stocks"],
    "메타": ["stocks"],
    "META": ["stocks"],
    "브로드컴": ["stocks"],
    "AVGO": ["stocks"],
    "AMD": ["stocks"],
    "TSMC": ["stocks"],
    "마이크론": ["stocks"],
    "MU": ["stocks"],
    "크라우드스트라이크": ["stocks"],
    "CRWD": ["stocks"],
    "팔로알토": ["stocks"],
    "PANW": ["stocks"],
    "서비스나우": ["stocks"],
    "NOW": ["stocks"],
    "세일즈포스": ["stocks"],
    "CRM": ["stocks"],
    "넷플릭스": ["stocks"],
    "NFLX": ["stocks"],
    "앱러빈": ["stocks"],
    "APP": ["stocks"],
    "로빈후드": ["stocks"],
    "HOOD": ["stocks"],
    "아이온큐": ["stocks"],
    "IONQ": ["stocks"],
    "에어비앤비": ["stocks"],
    "ABNB": ["stocks"],
    "월마트": ["stocks"],
    "WMT": ["stocks"],
    "맥도날드": ["stocks"],
    "MCD": ["stocks"],
    "나이키": ["stocks"],
    "NKE": ["stocks"],
    "코스트코": ["stocks"],
    "COST": ["stocks"],
    "카니발": ["stocks"],
    "CCL": ["stocks"],
    "노보노디스크": ["stocks"],
    "일라이릴리": ["stocks"],
    "LLY": ["stocks"],
    "버크셔": ["stocks", "investment"],
    "BRK": ["stocks", "investment"],
    "ASML": ["stocks"],
    "피그마": ["stocks"],
    "웹툰": ["stocks"],
    "캐터필러": ["stocks"],
    "CAT": ["stocks"],
    "아이렌": ["stocks"],
    "IREN": ["stocks"],
    "샌디스크": ["stocks"],
    "SNDK": ["stocks"],
    "랙스페이스": ["stocks"],
    "RXT": ["stocks"],
    "힘스앤허스": ["stocks"],
    "HIMS": ["stocks"],
    "스페이스모바일": ["stocks"],
    "AST": ["stocks"],
    "록히드": ["stocks", "global-economy"],
    "방산주": ["stocks", "global-economy"],
    "SCHD": ["investment"],
    "ETF": ["investment"],
    "배당": ["investment"],
    "커버드콜": ["investment"],
    "레버리지": ["investment"],
    "비트코인": ["crypto"],
    "코인": ["crypto"],
    "USDC": ["crypto"],
    "스테이블": ["crypto"],
    "이란": ["global-economy"],
    "전쟁": ["global-economy"],
    "호르무즈": ["global-economy"],
    "관세": ["global-economy"],
    "트럼프": ["global-economy"],
    "희토류": ["global-economy"],
    "CPI": ["economic-policy"],
    "물가": ["economic-policy"],
    "환율": ["economic-policy"],
    "삼성전자": ["stocks"],
    "양자컴퓨터": ["stocks"],
    "AI 관련주": ["stocks"],
    "반도체": ["stocks"],
    "로봇": ["stocks"],
    "휴머노이드": ["stocks"],
    "데이터센터": ["stocks"],
    "클로드": ["stocks"],
    "앤트로픽": ["stocks"],
    "챗GPT": ["stocks"],
    "OpenAI": ["stocks"],
    "스포티파이": ["stocks"],
    "SPOT": ["stocks"],
    "써클": ["crypto"],
    "CRCL": ["crypto"],
}

# Files to EXCLUDE (sponsored content or already uploaded)
EXCLUDE_KEYWORDS_IN_FILENAME = [
    "겜스고",
    "비교원",
    "키움증권_개인연금",
    "직방_AI_중개사",
    "고향사랑기부제",
]

# Already uploaded article title keywords (to match and skip)
ALREADY_UPLOADED_KEYWORDS = [
    "로켓배송_없이_살_수_있나요_쿠팡",
    "록히드마틴_1년_50_이란_전쟁",
    "매출_83인데_주가는_-5_템퍼스AI",
    "폭락한_서비스나우_클로드_쇼크",
    "돌고_돌아_SCHD_미국_이란",
    "워런_버핏이_떠난_버크셔해서웨이",
    "178조_인수_포기했더니_주가",
    "마진_84인데_-40_폭락_앱러빈",
    "호르무즈_해협_봉쇄_전_세계",
    "주가_빠진_마이크로소프트_코파일럿",
    "클로드가_보안_AI를_만들었다고_크라우드스트라이크",
    "팔란티어는_왜_방산주인가",
    "국장_보고_열받아서",
    "AI_칩_매출_2배_폭등_구글_오픈AI가_줄_서는_회사_브로드컴",
    "여보_미안해_엔비디아_주식_1800_수익",
]


def should_exclude(filename):
    """Check if file should be excluded."""
    for kw in EXCLUDE_KEYWORDS_IN_FILENAME:
        if kw in filename:
            return True
    for kw in ALREADY_UPLOADED_KEYWORDS:
        if kw in filename:
            return True
    return False


def check_sponsored(content):
    """Check if content is sponsored."""
    first_500 = content[:500]
    markers = ["원고료를 받아", "원고료를 지급", "소정의 원고료", "업체로부터"]
    return any(m in first_500 for m in markers)


def extract_date_from_filename(filename):
    """Extract date from filename for sorting."""
    match = re.match(r"(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2})", filename)
    if match:
        date_str = match.group(1)
        time_str = match.group(2)
        try:
            return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            pass
    # For files like "12분 전_..." or "23시간 전_..."
    if "분 전" in filename or "시간 전" in filename:
        return datetime(2026, 3, 7)  # Today
    return datetime(2025, 1, 1)  # Fallback


def get_title(md):
    """Extract H1 title from markdown."""
    for line in md.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def get_excerpt(md):
    """Extract first meaningful paragraph as excerpt."""
    lines = md.strip().split("\n")
    found_separator = False
    for line in lines:
        if line.strip() == "---":
            found_separator = True
            continue
        if found_separator and line.strip() and not line.startswith("#"):
            # Skip metadata lines and empty markers
            if line.strip() in ("", "\u200b") or line.startswith("- URL:") or line.startswith("- "):
                continue
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", line.strip())
            text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
            if len(text) > 10:
                return text[:200]
    return ""


def get_categories(filename, content):
    """Determine categories based on keywords."""
    cats = set()
    combined = filename + " " + content[:2000]
    for keyword, cat_slugs in KEYWORD_CATEGORIES.items():
        if keyword in combined:
            for slug in cat_slugs:
                cats.add(CATEGORIES[slug])
    if not cats:
        cats.add(CATEGORIES["stocks"])
    return list(cats)


def inline_format(text):
    """Convert inline markdown to HTML."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def md_to_html(md):
    """Convert markdown to HTML, skipping metadata header."""
    lines = md.strip().split("\n")
    html_parts = []
    in_table = False
    table_rows = []
    in_list = False
    list_items = []
    skip_header = True

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            return ""
        header = table_rows[0]
        body = table_rows[2:] if len(table_rows) > 2 else []
        out = '<table class="wp-block-table"><thead><tr>'
        for cell in header:
            out += f"<th>{cell.strip()}</th>"
        out += "</tr></thead><tbody>"
        for row in body:
            out += "<tr>"
            for cell in row:
                out += f"<td>{cell.strip()}</td>"
            out += "</tr>"
        out += "</tbody></table>"
        in_table = False
        table_rows.clear()
        return out

    def flush_list():
        nonlocal in_list, list_items
        if not list_items:
            return ""
        out = "<ul>"
        for item in list_items:
            out += f"<li>{inline_format(item)}</li>"
        out += "</ul>"
        in_list = False
        list_items.clear()
        return out

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip metadata header (title, URL, author, date lines before ---)
        if skip_header:
            if line.strip() == "---":
                skip_header = False
                i += 1
                continue
            i += 1
            continue

        # Skip empty unicode markers
        if line.strip() in ("\u200b", ""):
            html_parts.append(flush_list())
            i += 1
            continue

        # Skip lines that are just URLs to naver blog
        if line.strip().startswith("https://blog.naver.com"):
            i += 1
            continue

        # Skip "- URL:", "- 작성자:", "- 날짜:" metadata
        if re.match(r"^-\s+(URL|작성자|날짜):", line):
            i += 1
            continue

        # Horizontal rule
        if line.strip() == "---":
            html_parts.append(flush_list())
            html_parts.append(flush_table())
            html_parts.append("<hr/>")
            i += 1
            continue

        # Table
        if "|" in line and line.strip().startswith("|"):
            html_parts.append(flush_list())
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            table_rows.append(cells)
            in_table = True
            i += 1
            continue
        elif in_table:
            html_parts.append(flush_table())

        # Headers
        if line.startswith("# "):
            html_parts.append(flush_list())
            i += 1
            continue
        if line.startswith("## "):
            html_parts.append(flush_list())
            html_parts.append(f"<h2>{inline_format(line[3:].strip())}</h2>")
            i += 1
            continue
        if line.startswith("### "):
            html_parts.append(flush_list())
            html_parts.append(f"<h3>{inline_format(line[4:].strip())}</h3>")
            i += 1
            continue

        # List items
        if re.match(r"^[-*]\s", line.strip()):
            item = re.sub(r"^[-*]\s+", "", line.strip())
            list_items.append(item)
            in_list = True
            i += 1
            continue
        elif in_list:
            html_parts.append(flush_list())

        # Numbered list
        if re.match(r"^\d+\.\s", line.strip()):
            html_parts.append(flush_list())
            item = re.sub(r"^\d+\.\s+", "", line.strip())
            html_parts.append(f"<p>{inline_format(item)}</p>")
            i += 1
            continue

        # Q&A format (common in these articles)
        if line.strip().startswith("Q:") or line.strip().startswith("A:"):
            html_parts.append(f"<p><strong>{inline_format(line.strip())}</strong></p>")
            i += 1
            continue

        # Regular paragraph
        html_parts.append(f"<p>{inline_format(line.strip())}</p>")
        i += 1

    html_parts.append(flush_list())
    html_parts.append(flush_table())

    return "\n".join(p for p in html_parts if p)


def generate_image_prompt(title, content_preview):
    """Generate an image prompt based on article title."""
    # Extract key topic from title for targeted prompt
    title_lower = title.lower()

    # Common patterns
    if any(k in title for k in ["엔비디아", "NVDA", "NVIDIA"]):
        return "A cute stickman looking at a giant GPU chip with green glow, stock chart arrows and dollar signs floating around, simple minimal line drawing style, white background"
    if any(k in title for k in ["테슬라", "TSLA", "전기차"]):
        return "A stickman driving a futuristic electric car with a robot standing next to it, stock chart in the background, simple minimal line drawing style, white background"
    if any(k in title for k in ["애플", "AAPL"]):
        return "A stickman holding a glowing apple-shaped device with AI sparkles, stock chart trending upward behind, simple minimal line drawing style, white background"
    if any(k in title for k in ["팔란티어", "PLTR"]):
        return "A stickman general looking at a big tactical data screen with satellite imagery and analysis graphs, military and tech icons around, simple minimal line drawing style, white background"
    if any(k in title for k in ["아마존", "AMZN"]):
        return "A stickman surrounded by delivery boxes and cloud computing servers, with a stock chart showing growth, simple minimal line drawing style, white background"
    if any(k in title for k in ["구글", "알파벳", "GOOGL"]):
        return "A stickman using a colorful search engine with AI brain icon above, data analytics dashboard in background, simple minimal line drawing style, white background"
    if any(k in title for k in ["마이크로소프트", "MSFT"]):
        return "A stickman at a desk with Windows logo computer, AI copilot robot assistant nearby, stock chart on wall, simple minimal line drawing style, white background"
    if any(k in title for k in ["AMD"]):
        return "A stickman comparing two computer chips side by side, one larger and one smaller, with performance bar charts, simple minimal line drawing style, white background"
    if any(k in title for k in ["TSMC", "파운드리"]):
        return "A stickman in a clean room suit making tiny computer chips on a conveyor belt, factory and stock chart in background, simple minimal line drawing style, white background"
    if any(k in title for k in ["마이크론", "메모리", "HBM", "샌디스크"]):
        return "A stickman stacking memory chip blocks into a tall tower, with AI and data center icons nearby, simple minimal line drawing style, white background"
    if any(k in title for k in ["비트코인", "코인", "BTCI"]):
        return "A stickman riding a roller coaster shaped like a Bitcoin price chart, with coins flying around, simple minimal line drawing style, white background"
    if any(k in title for k in ["써클", "USDC", "스테이블"]):
        return "A stickman balancing on a stable coin platform while crypto waves crash around, with dollar signs on the coin, simple minimal line drawing style, white background"
    if any(k in title for k in ["ETF", "SCHD", "배당", "월배당"]):
        return "A happy stickman sitting on a growing pile of coins with dividend money raining down, holding an umbrella made of stock certificates, simple minimal line drawing style, white background"
    if any(k in title for k in ["레버리지", "2배", "3배"]):
        return "A stickman on a see-saw that amplifies up and down movements dramatically, with 2x and 3x labels, stock charts showing extreme swings, simple minimal line drawing style, white background"
    if any(k in title for k in ["커버드콜", "SPYI", "QQQI", "QDVO"]):
        return "A stickman with a safety net below catching falling coins while a stock chart moves sideways, monthly income calendar on wall, simple minimal line drawing style, white background"
    if any(k in title for k in ["방산", "록히드", "전쟁", "이란"]):
        return "A stickman looking at a big screen showing military jets and defense equipment, with stock arrows going up, world map with tension markers, simple minimal line drawing style, white background"
    if any(k in title for k in ["관세", "트럼프", "폭락"]):
        return "A worried stickman watching stock charts crash like dominos, with trade war barriers and tariff signs, simple minimal line drawing style, white background"
    if any(k in title for k in ["희토류"]):
        return "A stickman digging for rare earth minerals with Chinese and American flags in background, supply chain icons, simple minimal line drawing style, white background"
    if any(k in title for k in ["CPI", "물가", "인플레이션"]):
        return "A stickman looking at rising price tags on everyday items, with a government building and inflation chart in background, simple minimal line drawing style, white background"
    if any(k in title for k in ["환율", "달러"]):
        return "A stickman on a currency exchange seesaw between dollar and won signs, with exchange rate chart, simple minimal line drawing style, white background"
    if any(k in title for k in ["로봇", "휴머노이드", "피지컬 AI"]):
        return "A stickman watching a humanoid robot working in a factory, with AI and automation icons, futuristic setting, simple minimal line drawing style, white background"
    if any(k in title for k in ["양자컴퓨터", "아이온큐", "IONQ"]):
        return "A stickman looking amazed at a glowing quantum computer with qubits floating around, futuristic lab setting, simple minimal line drawing style, white background"
    if any(k in title for k in ["클로드", "앤트로픽", "챗GPT", "AI 에이전트"]):
        return "A stickman talking to two competing AI robot assistants, with tech company logos and disruption lightning bolts, simple minimal line drawing style, white background"
    if any(k in title for k in ["보안", "사이버", "팔로알토"]):
        return "A stickman security guard with digital shield blocking cyber attack arrows, with lock icons and firewall, simple minimal line drawing style, white background"
    if any(k in title for k in ["넷플릭스", "스포티파이", "스트리밍"]):
        return "A stickman watching multiple streaming screens with popcorn, subscriber count going up on a chart, simple minimal line drawing style, white background"
    if any(k in title for k in ["월마트", "코스트코", "유통"]):
        return "A stickman pushing a giant shopping cart through a warehouse store, with revenue chart climbing, simple minimal line drawing style, white background"
    if any(k in title for k in ["맥도날드", "배당주"]):
        return "A stickman eating a burger while dividends rain down like fries, steady growth chart in background, simple minimal line drawing style, white background"
    if any(k in title for k in ["나이키", "스포츠"]):
        return "A stickman running with a swoosh logo, passing by stock chart milestones, sports equipment around, simple minimal line drawing style, white background"
    if any(k in title for k in ["에어비앤비", "ABNB"]):
        return "A stickman hosting guests at a tiny house with a for-rent sign, stock chart and travel icons, simple minimal line drawing style, white background"
    if any(k in title for k in ["비만", "GLP", "마운자로", "위고비"]):
        return "A stickman doctor showing a weight loss injection to patients waiting in line, pharma stock chart rising, simple minimal line drawing style, white background"
    if any(k in title for k in ["카니발", "크루즈"]):
        return "A stickman on a cruise ship deck with stock chart waves in the ocean, vacation and money icons, simple minimal line drawing style, white background"
    if any(k in title for k in ["ASML", "EUV"]):
        return "A stickman operating a giant laser machine making tiny chips, with Dutch flag and semiconductor icons, simple minimal line drawing style, white background"
    if any(k in title for k in ["피그마", "어도비"]):
        return "A stickman designer using colorful design tools on screen, competing with another designer, tech stock chart nearby, simple minimal line drawing style, white background"
    if any(k in title for k in ["웹툰"]):
        return "A stickman reading comics on a phone screen with Disney castle in background, stock chart with entertainment icons, simple minimal line drawing style, white background"
    if any(k in title for k in ["캐터필러", "CAT"]):
        return "A stickman driving a yellow bulldozer building a data center, construction and infrastructure icons, simple minimal line drawing style, white background"
    if any(k in title for k in ["힘스앤허스", "HIMS"]):
        return "A stickman at a telehealth pharmacy counter with prescription bottles, stock chart showing a dramatic dip, simple minimal line drawing style, white background"
    if any(k in title for k in ["비욘드미트", "공매도", "숏스퀴즈"]):
        return "A stickman squeezing a bear character (short seller) while stock chart shoots upward dramatically, simple minimal line drawing style, white background"
    if any(k in title for k in ["수익 인증", "투자하는 방법", "투자 방법"]):
        return "A stickman proudly showing a portfolio screen with green gains, teaching another stickman about investing, simple minimal line drawing style, white background"
    if any(k in title for k in ["삼성전자"]):
        return "A stickman looking at Korean and US stock charts side by side, memory chips and smartphone icons between them, simple minimal line drawing style, white background"
    if any(k in title for k in ["스페이스", "우주"]):
        return "A stickman looking through telescope at satellites orbiting earth, with rocket and space tech stock chart, simple minimal line drawing style, white background"
    if any(k in title for k in ["세일즈포스"]):
        return "A stickman cloud surfing on CRM data, with AI sparkles and enterprise software icons, simple minimal line drawing style, white background"
    if any(k in title for k in ["인텔"]):
        return "A stickman trying to lift a heavy old chip while new lighter chips float nearby, stock chart with sudden spike, simple minimal line drawing style, white background"
    if any(k in title for k in ["로빈후드"]):
        return "A stickman in Robin Hood hat trading stocks on a phone app, crypto coins and stock icons flying around, simple minimal line drawing style, white background"
    if any(k in title for k in ["블로그 리포트", "마이 블로그"]):
        return "A stickman looking at a year-end blog analytics dashboard with charts and stats, celebration confetti, simple minimal line drawing style, white background"

    # Default fallback
    return "A curious stickman analyzing stock charts on multiple screens with magnifying glass, bull and bear icons nearby, investment and finance theme, simple minimal line drawing style, white background"


def generate_image(prompt):
    """Generate image via Recraft API."""
    data = json.dumps({
        "prompt": prompt,
        "model": "recraftv3",
        "style": "digital_illustration",
        "substyle": "hand_drawn",
        "size": "1820x1024",
        "n": 1,
    }).encode("utf-8")

    req = urllib.request.Request(
        RECRAFT_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {RECRAFT_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
            return result["data"][0]["url"]
    except urllib.error.HTTPError as e:
        error = e.read().decode()
        print(f"  Recraft error: {e.code} - {error[:300]}")
        return None
    except Exception as e:
        print(f"  Recraft error: {e}")
        return None


def download_image(url):
    """Download image to temp file."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.write(data)
    tmp.close()
    return tmp.name


def upload_to_wordpress(filepath, title):
    """Upload image to WordPress media library."""
    auth = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()

    with open(filepath, "rb") as f:
        image_data = f.read()

    hash_suffix = hashlib.md5(title.encode()).hexdigest()[:8]
    filename = f"featured-{hash_suffix}.png"

    for attempt in range(3):
        try:
            r = urllib.request.Request(
                f"{WP_API}/media",
                data=image_data,
                headers={
                    "Authorization": f"Basic {auth}",
                    "Content-Type": "image/png",
                    "Content-Disposition": f'attachment; filename="{filename}"',
                },
                method="POST",
            )
            with urllib.request.urlopen(r, timeout=90) as resp:
                result = json.loads(resp.read().decode())
                return result["id"]
        except urllib.error.HTTPError as e:
            error = e.read().decode()
            print(f"  WP upload error: {e.code} - {error[:200]}")
            return None
        except Exception as e:
            print(f"  WP upload timeout (attempt {attempt+1}/3): {e}")
            if attempt < 2:
                time.sleep(5)
    return None


def set_featured_image(post_id, media_id):
    """Set featured image for a post."""
    auth = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
    data = json.dumps({"featured_media": media_id}).encode("utf-8")

    req = urllib.request.Request(
        f"{WP_API}/posts/{post_id}",
        data=data,
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result.get("featured_media") == media_id
    except urllib.error.HTTPError as e:
        error = e.read().decode()
        print(f"  WP featured error: {e.code} - {error[:200]}")
        return False


def create_post(title, content, excerpt, categories, date, status="future"):
    """Create a WordPress post via REST API."""
    auth = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()

    data = {
        "title": title,
        "content": content,
        "excerpt": excerpt,
        "categories": categories,
        "status": status,
        "date": date,
    }

    json_data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        f"{WP_API}/posts",
        data=json_data,
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            return {"id": result["id"], "slug": result["slug"], "status": result["status"]}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        return {"error": f"{e.code}: {error_body[:200]}"}


def main():
    # 1. Collect all articles
    files = sorted(ARTICLES_DIR.glob("*.md"))
    print(f"Total articles found: {len(files)}")

    # 2. Filter
    articles = []
    skipped_sponsored = 0
    skipped_uploaded = 0
    skipped_exclude = 0

    for f in files:
        fname = f.name

        # Check exclusion by filename keywords
        if should_exclude(fname):
            if any(kw in fname for kw in ALREADY_UPLOADED_KEYWORDS):
                skipped_uploaded += 1
            else:
                skipped_exclude += 1
            continue

        content = f.read_text(encoding="utf-8")

        # Check sponsored content
        if check_sponsored(content):
            skipped_sponsored += 1
            continue

        title = get_title(content)
        orig_date = extract_date_from_filename(fname)

        articles.append({
            "file": f,
            "title": title,
            "content": content,
            "orig_date": orig_date,
        })

    # Sort by original date (oldest first)
    articles.sort(key=lambda a: a["orig_date"])

    print(f"Filtered: {len(articles)} articles to upload")
    print(f"  Skipped (already uploaded): {skipped_uploaded}")
    print(f"  Skipped (sponsored): {skipped_sponsored}")
    print(f"  Skipped (excluded): {skipped_exclude}")

    # 3. Generate schedule (3 per day)
    start = datetime.strptime(START_DATE, "%Y-%m-%d")
    schedule = []
    for i, article in enumerate(articles):
        day_offset = i // 3
        time_index = i % 3
        pub_date = start + timedelta(days=day_offset)
        pub_datetime = f"{pub_date.strftime('%Y-%m-%d')}T{SCHEDULE_TIMES[time_index]}"
        schedule.append((article, pub_datetime))

    last_date = start + timedelta(days=(len(articles) - 1) // 3)
    print(f"\nSchedule: {START_DATE} ~ {last_date.strftime('%Y-%m-%d')}")
    print(f"  {len(articles)} articles over {(len(articles) - 1) // 3 + 1} days\n")

    # Show schedule preview
    print("=" * 70)
    print("SCHEDULE PREVIEW (first 15)")
    print("=" * 70)
    for i, (article, pub_dt) in enumerate(schedule[:15]):
        print(f"  {pub_dt} | {article['title'][:50]}")
    if len(schedule) > 15:
        print(f"  ... and {len(schedule) - 15} more")
    print("=" * 70)

    # Auto-confirm (use --dry-run to preview only)
    import sys
    if "--dry-run" in sys.argv:
        print("\nDry run mode. Exiting.")
        return

    # Resume support: --resume N skips first N articles
    resume_from = 0
    for arg in sys.argv:
        if arg.startswith("--resume="):
            resume_from = int(arg.split("=")[1])
    if resume_from:
        print(f"\nResuming from article #{resume_from + 1} (skipping first {resume_from})")
        schedule = schedule[resume_from:]

    print("\nStarting upload...")

    # 4. Process each article
    success = 0
    fail = 0
    results = []

    for i, (article, pub_datetime) in enumerate(schedule):
        title = article["title"]
        print(f"\n[{i+1}/{len(schedule)}] {title[:55]}")
        print(f"  Scheduled: {pub_datetime}")

        # Convert to HTML
        html = md_to_html(article["content"])
        excerpt = get_excerpt(article["content"])
        categories = get_categories(article["file"].name, article["content"])

        # Generate image
        print("  Generating image...")
        prompt = generate_image_prompt(title, article["content"][:500])
        image_url = generate_image(prompt)

        media_id = None
        if image_url:
            print("  Downloading image...")
            filepath = download_image(image_url)
            print("  Uploading to WordPress...")
            media_id = upload_to_wordpress(filepath, title)
            os.unlink(filepath)
            if not media_id:
                print("  WARN: image upload failed, continuing without image")
        else:
            print("  WARN: image generation failed, continuing without image")

        # Create post
        print("  Creating scheduled post...")
        result = create_post(title, html, excerpt, categories, pub_datetime)

        if "error" in result:
            print(f"  ERROR: {result['error']}")
            fail += 1
        else:
            post_id = result["id"]
            print(f"  OK: id={post_id}, status={result['status']}")

            # Set featured image
            if media_id:
                ok = set_featured_image(post_id, media_id)
                if ok:
                    print(f"  Featured image set (media_id={media_id})")
                else:
                    print(f"  WARN: featured image may not have set correctly")

            success += 1
            results.append({
                "id": post_id,
                "title": title,
                "date": pub_datetime,
                "media_id": media_id,
            })

        # Rate limit (Recraft: be nice)
        if i < len(schedule) - 1:
            time.sleep(3)

    # Summary
    print(f"\n{'=' * 70}")
    print(f"DONE: {success} success, {fail} failed out of {len(schedule)} total")
    print(f"{'=' * 70}")

    # Save results
    results_file = Path(__file__).parent / "batch-upload-results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Results saved to: {results_file}")


if __name__ == "__main__":
    main()
