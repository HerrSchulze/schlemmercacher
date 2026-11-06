"""Extrahiert WordPress-Posts via REST-API und generiert eine statische HTML-Seite."""

import html
import json
import os
import re
import shutil
import urllib.error
import urllib.request
from datetime import datetime

WP_API = "https://schlemmercacher.de/wp-json/wp/v2/posts"
OUT_DIR = os.path.join(os.path.dirname(__file__), "_site")
POSTS_DIR = os.path.join(OUT_DIR, "posts")
PER_PAGE = 100


def fetch_all_posts():
    posts = []
    page = 1
    while True:
        url = f"{WP_API}?per_page={PER_PAGE}&page={page}&_fields=id,date,slug,title,content,excerpt,categories,tags,link"
        req = urllib.request.Request(url, headers={"User-Agent": "schlemmercacher-static-export/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if page > 1 and err.code in (400, 404):
                break  # jenseits des letzten Blattes -> Pagination beenden
            raise
        if not data:
            break
        posts.extend(data)
        print(f"Seite {page}: {len(data)} Posts geladen (gesamt: {len(posts)})")
        page += 1
    return posts


def clean_excerpt(raw):
    if not raw:
        return ""
    text = re.sub(r"<[^>]+>", "", raw)
    text = html.unescape(text)
    return text.strip()


def slug_filename(post):
    slug = post.get("slug") or f"post-{post['id']}"
    safe = re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-")
    return safe or f"post-{post['id']}"


def fmt_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        return dt.strftime("%d.%m.%Y")
    except (ValueError, TypeError):
        return date_str


def render_post_page(post):
    title = html.unescape(post["title"]["rendered"])
    content = post["content"]["rendered"]
    date = fmt_date(post["date"])
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | Schlemmercacher Archiv</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<header>
<h1><a href="../index.html">Schlemmercacher Archiv</a></h1>
<nav><a href="../index.html">Zurück zur Übersicht</a></nav>
</header>
<main>
<article>
<time>{date}</time>
<h1>{html.escape(title)}</h1>
<div class="content">{content}</div>
</article>
</main>
</body>
</html>"""


def render_index(posts):
    items = []
    for post in posts:
        title = html.unescape(post["title"]["rendered"])
        date = fmt_date(post["date"])
        excerpt = clean_excerpt(post.get("excerpt", {}).get("rendered", ""))
        fname = slug_filename(post)
        items.append(f"""
<li>
<time>{date}</time>
<h2><a href="posts/{fname}.html">{html.escape(title)}</a></h2>
<p class="excerpt">{html.escape(excerpt)[:300]}{'…' if len(excerpt) > 300 else ''}</p>
</li>""")
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Schlemmercacher Archiv — Blog-Posts</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header>
<h1>Schlemmercacher Archiv</h1>
<p>Statisch archivierte Beiträge des ehemaligen WordPress-Blogs.</p>
</header>
<main>
<h2>Beiträge ({len(posts)})</h2>
<ul class="post-list">{"".join(items)}</ul>
</main>
</body>
</html>"""


CSS = """* {{ box-sizing: border-box; }}
body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; max-width: 720px; margin: 0 auto; padding: 1.5rem; line-height: 1.6; color: #222; background: #fff; }}
header {{ border-bottom: 2px solid #999; padding-bottom: 1rem; margin-bottom: 1.5rem; }}
header h1 {{ margin: 0; font-size: 1.75rem; }}
header h1 a {{ color: #222; text-decoration: none; }}
nav a {{ color: #555; text-decoration: none; }}
nav a:hover {{ text-decoration: underline; }}
time {{ display: block; color: #666; font-size: 0.9rem; margin-bottom: 0.25rem; }}
h1 {{ font-size: 1.5rem; margin: 0 0 1rem 0; }}
h2 {{ font-size: 1.25rem; margin: 0; }}
h2 a {{ color: #222; text-decoration: none; }}
h2 a:hover {{ color: #0066cc; }}
.post-list {{ list-style: none; padding: 0; }}
.post-list li {{ border-bottom: 1px solid #ddd; padding: 1rem 0; }}
.post-list li:last-child {{ border-bottom: none; }}
.excerpt {{ color: #555; font-size: 0.95rem; margin: 0.5rem 0 0 0; }}
.content {{ margin-top: 1rem; }}
.content p {{ margin: 1rem 0; }}
.content img {{ max-width: 100%; height: auto; display: block; margin: 1rem auto; }}
.content a {{ color: #0066cc; }}
@media (max-width: 600px) {{ body {{ padding: 1rem; }} }}
"""


def main():
    os.makedirs(POSTS_DIR, exist_ok=True)
    posts = fetch_all_posts()
    posts.sort(key=lambda p: p.get("date", ""), reverse=True)

    with open(os.path.join(OUT_DIR, "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS)

    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_index(posts))

    # statische Hilfsdateien ins Build-Verzeichnis kopieren
    for extra in ("404.html", "CNAME"):
        src = os.path.join(os.path.dirname(__file__), extra)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(OUT_DIR, extra))

    for post in posts:
        fname = slug_filename(post)
        with open(os.path.join(POSTS_DIR, f"{fname}.html"), "w", encoding="utf-8") as f:
            f.write(render_post_page(post))

    print(f"\nFertig: {len(posts)} Posts in {OUT_DIR} generiert.")


if __name__ == "__main__":
    main()
