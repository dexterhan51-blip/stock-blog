#!/usr/bin/env python3
"""Markdown 원고를 WordPress REST API로 일괄 업로드"""

import os
import re
import json
import urllib.request
import urllib.error
import base64
from pathlib import Path

WP_API = "https://wordpress-1592891-6259767.cloudwaysapps.com/wp-json/wp/v2"
WP_USER = "dexterhan51@gmail.com"
WP_APP_PASSWORD = "pkOC VTKe 9VuM rhLn 4yuz UGPK"

# Category mapping (slug -> id)
CATEGORIES = {
    "stocks": 2,
    "real-estate": 3,
    "economic-policy": 4,
    "investment": 5,
    "global-economy": 6,
    "daily-economy": 7,
    "crypto": 8,
}

# Article -> category mapping
ARTICLE_CATEGORIES = {
    "쿠팡": ["stocks"],
    "방산주": ["stocks", "global-economy"],
    "템퍼스AI": ["stocks"],
    "서비스나우": ["stocks"],
    "SCHD": ["investment"],
    "버크셔해서웨이": ["stocks", "investment"],
    "넷플릭스": ["stocks"],
    "앱러빈": ["stocks"],
    "호르무즈": ["global-economy"],
    "마이크로소프트": ["stocks"],
    "크라우드스트라이크": ["stocks"],
    "팔란티어": ["stocks"],
    "삼성전자": ["stocks"],
    "브로드컴": ["stocks"],
    "엔비디아": ["stocks", "investment"],
}

# Date mapping from filename
DATE_MAP = {
    "2026-02-28": "2026-02-28T09:00:00",
    "2026-03-01": "2026-03-01T09:00:00",
    "2026-03-02": "2026-03-02T09:00:00",
    "2026-03-03": "2026-03-03T09:00:00",
    "2026-03-04": "2026-03-04T09:00:00",
    "2026-03-05": "2026-03-05T09:00:00",
}


def md_to_html(md: str) -> str:
    """Simple markdown to HTML conversion."""
    lines = md.strip().split("\n")
    html_parts = []
    in_table = False
    table_rows = []
    in_list = False
    list_items = []

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            return ""
        # First row is header
        header = table_rows[0]
        body = table_rows[2:]  # Skip separator row
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
        table_rows = []
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
        list_items = []
        return out

    def inline_format(text: str) -> str:
        # Bold
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        # Links
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
        return text

    i = 0
    while i < len(lines):
        line = lines[i]

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
            # Skip H1 (it's the title)
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

        # Arrow flow (->)
        if line.strip().startswith("->"):
            text = line.strip().replace("->", "").strip()
            html_parts.append(f"<p>→ {inline_format(text)}</p>")
            i += 1
            continue

        # Empty line
        if not line.strip():
            html_parts.append(flush_list())
            i += 1
            continue

        # Regular paragraph
        html_parts.append(f"<p>{inline_format(line.strip())}</p>")
        i += 1

    # Flush remaining
    html_parts.append(flush_list())
    html_parts.append(flush_table())

    return "\n".join(p for p in html_parts if p)


def get_title(md: str) -> str:
    """Extract H1 title from markdown."""
    for line in md.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def get_excerpt(md: str) -> str:
    """Extract first paragraph after title as excerpt."""
    lines = md.strip().split("\n")
    found_title = False
    for line in lines:
        if line.startswith("# "):
            found_title = True
            continue
        if found_title and line.strip() and not line.startswith("#") and line.strip() != "---":
            # Clean markdown formatting
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", line.strip())
            return text[:200]
    return ""


def get_categories_for_article(filename, content):
    """Determine categories based on content."""
    cats = set()
    for keyword, cat_slugs in ARTICLE_CATEGORIES.items():
        if keyword in filename or keyword in content:
            for slug in cat_slugs:
                cats.add(CATEGORIES[slug])
    if not cats:
        cats.add(CATEGORIES["stocks"])  # Default
    return list(cats)


def get_date(filename):
    """Extract date from filename."""
    match = re.match(r"(\d{4}-\d{2}-\d{2})", filename)
    if match:
        return DATE_MAP.get(match.group(1))
    return None


def create_post(title, content, excerpt, categories, date=None, status="publish"):
    """Create a WordPress post via REST API."""
    auth = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()

    data = {
        "title": title,
        "content": content,
        "excerpt": excerpt,
        "categories": categories,
        "status": status,
    }
    if date:
        data["date"] = date

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
    rewritten_dir = Path("/Users/dexterhan/Documents/Projects/tools/author/output/rewritten")
    files = sorted(rewritten_dir.glob("*.md"))

    print(f"Found {len(files)} articles to upload\n")

    for f in files:
        md = f.read_text(encoding="utf-8")
        title = get_title(md)
        html = md_to_html(md)
        excerpt = get_excerpt(md)
        categories = get_categories_for_article(f.name, md)
        date = get_date(f.name)

        print(f"Uploading: {title[:60]}...")
        result = create_post(title, html, excerpt, categories, date)

        if "error" in result:
            print(f"  ERROR: {result['error']}")
        else:
            print(f"  OK: id={result['id']}, slug={result['slug']}, status={result['status']}")

    print("\nDone!")


if __name__ == "__main__":
    main()
