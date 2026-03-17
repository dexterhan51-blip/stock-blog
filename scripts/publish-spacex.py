#!/usr/bin/env python3
"""SpaceX IPO 글 단건 발행 — Recraft 이미지 생성 + WordPress 즉시 발행"""

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
from datetime import datetime

# === CONFIG ===
RECRAFT_API_KEY = "AB96m9eEZ17sJxnjrVUoGVF3ZWlOXgjuyz6N4oWckeS22peD4bDjnINirB8JlnaC"
RECRAFT_URL = "https://external.api.recraft.ai/v1/images/generations"

WP_API = "https://wordpress-1592891-6259767.cloudwaysapps.com/wp-json/wp/v2"
WP_USER = "dexterhan51@gmail.com"
WP_APP_PASSWORD = "pkOC VTKe 9VuM rhLn 4yuz UGPK"

HTML_FILE = Path("/Users/dexterhan/Documents/Projects/tools/naver-blog-crawler/output/gjwlh_rewrite_01_spacex.html")

# Category IDs
CATEGORIES = [2]  # stocks


def extract_body_content(html_text):
    """Extract content between <body> tags, removing style/meta and outer wrapper tags."""
    # Get body content
    match = re.search(r"<body>(.*?)</body>", html_text, re.DOTALL)
    if not match:
        return html_text
    body = match.group(1).strip()

    # Remove the Naver image placeholders — replace with empty (we'll use featured image)
    body = re.sub(r'<div class="img-placeholder">.*?</div>', '', body, flags=re.DOTALL)

    # Remove inline style classes that WordPress won't understand, convert to WordPress-friendly HTML
    # Keep the semantic structure but clean up custom classes
    body = re.sub(r'<div class="highlight-box">', '<div style="background:#f0f4ff;border-radius:8px;padding:20px 24px;margin:24px 0;">', body)
    body = re.sub(r'<div class="qa">', '<div style="background:#fffbe6;border-left:4px solid #ffc107;padding:16px 20px;margin:20px 0;border-radius:0 8px 8px 0;">', body)
    body = re.sub(r'<div class="q">', '<p><strong>', body)
    body = re.sub(r'</div>\s*<div class="a">', '</strong></p><p style="color:#555;">', body)
    body = re.sub(r'<div class="checklist">', '<div style="background:#f9f9f9;padding:20px 24px;border-radius:8px;margin:24px 0;">', body)
    body = re.sub(r'<div class="disclaimer">', '<div style="background:#fff3f3;padding:16px;border-radius:8px;font-size:13px;color:#999;margin-top:48px;">', body)
    body = re.sub(r'<div class="tags">', '<div style="margin-top:32px;">', body)
    body = re.sub(r'<span>', '<span style="display:inline-block;background:#e8f0fe;color:#1a73e8;padding:4px 12px;border-radius:16px;font-size:13px;margin:4px 4px 4px 0;">', body)
    body = re.sub(r'<p class="meta">', '<p style="color:#888;font-size:14px;margin-bottom:32px;">', body)

    # Clean up table for WordPress
    body = body.replace('<table>', '<table style="width:100%;border-collapse:collapse;margin:20px 0;font-size:15px;">')
    body = body.replace('<th>', '<th style="background:#1a73e8;color:#fff;padding:10px 14px;text-align:left;">')
    body = body.replace('<td>', '<td style="padding:10px 14px;border-bottom:1px solid #e0e0e0;">')

    return body


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


def create_post(title, content, excerpt, categories, status="publish"):
    """Create a WordPress post via REST API."""
    auth = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()

    data = {
        "title": title,
        "content": content,
        "excerpt": excerpt,
        "categories": categories,
        "status": status,
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
            return {"id": result["id"], "slug": result["slug"], "status": result["status"], "link": result.get("link", "")}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        return {"error": f"{e.code}: {error_body[:200]}"}


def main():
    print("=" * 60)
    print("SpaceX IPO 글 발행")
    print("=" * 60)

    # 1. Read HTML file
    print(f"\n1. Reading: {HTML_FILE}")
    html_text = HTML_FILE.read_text(encoding="utf-8")

    title = "스페이스X IPO 임박! 스타링크 1,000만 돌파 시대, 관련주 총정리"
    excerpt = "2026년, 스페이스X를 둘러싼 분위기가 완전히 달라졌습니다. xAI 합병을 완료하며 기업가치가 약 1,750조 원에 달하는 메가 기업이 되었고, 스타링크 가입자는 1,000만 명을 돌파했습니다."

    # 2. Extract and clean body content
    print("2. Extracting body content...")
    content = extract_body_content(html_text)
    print(f"   Content length: {len(content)} chars")

    # 3. Generate featured image
    print("3. Generating featured image via Recraft...")
    prompt = "A stickman looking through telescope at satellites orbiting earth, with rocket and space tech stock chart, simple minimal line drawing style, white background"
    image_url = generate_image(prompt)

    media_id = None
    if image_url:
        print(f"   Image generated: {image_url[:80]}...")
        print("   Downloading...")
        filepath = download_image(image_url)
        print("   Uploading to WordPress...")
        media_id = upload_to_wordpress(filepath, title)
        os.unlink(filepath)
        if media_id:
            print(f"   Media ID: {media_id}")
        else:
            print("   WARN: image upload failed, continuing without image")
    else:
        print("   WARN: image generation failed, continuing without image")

    # 4. Create post
    print("4. Creating post (status=publish)...")
    result = create_post(title, content, excerpt, CATEGORIES)

    if "error" in result:
        print(f"   ERROR: {result['error']}")
        return

    post_id = result["id"]
    print(f"   OK: id={post_id}, status={result['status']}")
    print(f"   Link: {result.get('link', 'N/A')}")

    # 5. Set featured image
    if media_id:
        print("5. Setting featured image...")
        ok = set_featured_image(post_id, media_id)
        if ok:
            print(f"   Featured image set (media_id={media_id})")
        else:
            print("   WARN: featured image may not have set correctly")

    print(f"\n{'=' * 60}")
    print(f"DONE! Post ID: {post_id}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
