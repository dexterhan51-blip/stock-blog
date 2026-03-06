#!/usr/bin/env python3
"""Recraft API로 스틱맨 스타일 대표이미지 생성 -> WordPress 업로드 -> featured image 설정"""

import json
import urllib.request
import urllib.error
import base64
import time
import os
import tempfile

RECRAFT_API_KEY = "AB96m9eEZ17sJxnjrVUoGVF3ZWlOXgjuyz6N4oWckeS22peD4bDjnINirB8JlnaC"
RECRAFT_URL = "https://external.api.recraft.ai/v1/images/generations"

WP_API = "https://wordpress-1592891-6259767.cloudwaysapps.com/wp-json/wp/v2"
WP_USER = "dexterhan51@gmail.com"
WP_APP_PASSWORD = "pkOC VTKe 9VuM rhLn 4yuz UGPK"

# Post ID -> image prompt mapping
POSTS = [
    {
        "id": 14,
        "title": "쿠팡 Q4 실적",
        "prompt": "A cute stickman character excitedly receiving a rocket-fast delivery box at their doorstep, with a small chart showing revenue growth in the background, simple minimal line drawing style, white background"
    },
    {
        "id": 15,
        "title": "이란 공습 방산주",
        "prompt": "A stickman looking at a big screen showing fighter jets and military equipment, with stock chart arrows going up, another stickman taking notes, simple minimal line drawing style, white background"
    },
    {
        "id": 16,
        "title": "템퍼스AI 실적",
        "prompt": "A confused stickman looking at two arrows - one big green arrow labeled +83% going up and a small red arrow labeled -5% going down, with a DNA helix and AI brain icon, simple minimal line drawing style, white background"
    },
    {
        "id": 17,
        "title": "서비스나우 클로드 쇼크",
        "prompt": "A stickman robot labeled AI pushing over a row of software application icons like dominoes, with stock charts crashing down, another stickman watching in shock, simple minimal line drawing style, white background"
    },
    {
        "id": 18,
        "title": "SCHD ETF",
        "prompt": "A happy stickman sitting on a growing pile of coins with dividend money raining down, holding a shield labeled SCHD, while storm clouds with lightning hit tech stocks in the distance, simple minimal line drawing style, white background"
    },
    {
        "id": 19,
        "title": "버크셔해서웨이",
        "prompt": "A wise old stickman with glasses sitting on top of a giant building made of insurance, railroad, and energy blocks, waving goodbye while a younger stickman takes the wheel, simple minimal line drawing style, white background"
    },
    {
        "id": 20,
        "title": "넷플릭스 인수 포기",
        "prompt": "A stickman dropping a heavy bag labeled 178 trillion won and immediately jumping with joy as a stock chart rockets upward, a movie screen and popcorn in the corner, simple minimal line drawing style, white background"
    },
    {
        "id": 21,
        "title": "앱러빈 폭락",
        "prompt": "A stickman on a roller coaster that goes from a very high peak labeled 84% margin down a steep drop labeled -40%, with mobile phone ads floating around, simple minimal line drawing style, white background"
    },
    {
        "id": 22,
        "title": "호르무즈 해협 에너지",
        "prompt": "A stickman looking worried at a narrow water strait being blocked by barriers, oil barrels floating in the water, with gas pump price numbers rising, simple minimal line drawing style, white background"
    },
    {
        "id": 23,
        "title": "마이크로소프트 클로드",
        "prompt": "A stickman at a desk using a computer with Windows logo, secretly hiding a different AI tool under the desk, with a falling stock chart on the wall, simple minimal line drawing style, white background"
    },
    {
        "id": 24,
        "title": "크라우드스트라이크 보안",
        "prompt": "A stickman security guard with a shield blocking hackers, while an AI robot nearby reads code - they do different jobs, with a stock chart showing a dip, simple minimal line drawing style, white background"
    },
    {
        "id": 25,
        "title": "팔란티어 방산",
        "prompt": "A stickman general looking at a big tactical screen with satellite data and maps, connected to military equipment by data lines, with Pentagon building in corner, simple minimal line drawing style, white background"
    },
    {
        "id": 26,
        "title": "삼성전자 미장 관련주",
        "prompt": "A frustrated stickman looking at Korean stock market chart going down during daytime, then same stickman happily watching US stock market at night with memory chips and GPU icons, simple minimal line drawing style, white background"
    },
    {
        "id": 27,
        "title": "브로드컴 AI 칩",
        "prompt": "A stickman tailor custom-fitting a computer chip for big tech company logos (Google, Meta, OpenAI) waiting in line, with revenue chart doubling, simple minimal line drawing style, white background"
    },
    {
        "id": 28,
        "title": "엔비디아 수익 후회",
        "prompt": "A sad stickman looking at a tiny coin that grew into a small pile, imagining a thought bubble where the same coin became a mountain of money, with NVIDIA GPU chip icon, simple minimal line drawing style, white background"
    },
]


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
        print(f"  Error: {e}")
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

    # ASCII-safe filename
    import hashlib
    hash_suffix = hashlib.md5(title.encode()).hexdigest()[:8]
    filename = f"featured-{hash_suffix}.png"

    req = urllib.request.Request(
        f"{WP_API}/media",
        data=image_data,
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "image/png",
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result["id"]
    except urllib.error.HTTPError as e:
        error = e.read().decode()
        print(f"  WP upload error: {e.code} - {error[:200]}")
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


def main():
    print(f"Generating images for {len(POSTS)} posts\n")

    for i, post in enumerate(POSTS):
        print(f"[{i+1}/{len(POSTS)}] {post['title']}")

        # 1. Generate image
        print("  Generating image...")
        image_url = generate_image(post["prompt"])
        if not image_url:
            print("  SKIP - image generation failed")
            continue

        # 2. Download
        print("  Downloading...")
        filepath = download_image(image_url)

        # 3. Upload to WordPress
        print("  Uploading to WordPress...")
        media_id = upload_to_wordpress(filepath, post["title"])
        os.unlink(filepath)  # cleanup

        if not media_id:
            print("  SKIP - upload failed")
            continue

        # 4. Set as featured image
        print("  Setting featured image...")
        ok = set_featured_image(post["id"], media_id)
        if ok:
            print(f"  OK (media_id={media_id})")
        else:
            print(f"  WARN - may not have set correctly")

        # Rate limit
        if i < len(POSTS) - 1:
            time.sleep(2)

    print("\nDone!")


if __name__ == "__main__":
    main()
