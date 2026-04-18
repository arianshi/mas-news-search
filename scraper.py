from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import os

BASE_URL = "https://www.mas.gov.sg"
CACHE_FILE = os.path.join(os.path.dirname(__file__), "news_cache.json")

NEWS_CATEGORIES = {
    "media-releases": "/news/media-releases",
    "speeches": "/news/speeches",
    "monetary-policy": "/news/monetary-policy-statements",
    "consultations": "/news/consultations",
    "all": "/news",
}


def fetch_news(category="all", pages=1):
    """Fetch news articles from MAS website using a headless browser."""
    path = NEWS_CATEGORIES.get(category, NEWS_CATEGORIES["all"])
    articles = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for page_num in range(1, pages + 1):
            url = f"{BASE_URL}{path}"
            if page_num > 1:
                url += f"?page={page_num}"

            print(f"Loading {url} ...")
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception as e:
                print(f"Error loading page {page_num}: {e}")
                break

            # Detect maintenance mode
            title = page.title()
            if "maintenance" in title.lower():
                print("MAS website is currently under maintenance. Please try again later.")
                break

            items = _parse_articles(page)
            if not items:
                print(f"No articles found on page {page_num} — site may still be loading or structure has changed.")
                break

            articles.extend(items)
            print(f"Page {page_num}: found {len(items)} articles")

        browser.close()

    return articles


def _parse_articles(page):
    """Extract articles from the rendered MAS news page."""
    articles = []

    # Try multiple selector patterns used by MAS
    selectors = [
        ".mas-results-list__item",
        ".news-listing__item",
        "article",
        ".search-result-item",
        "[class*='news-item']",
        "[class*='result-item']",
    ]

    for selector in selectors:
        items = page.query_selector_all(selector)
        if items:
            for item in items:
                title_el = item.query_selector("h2, h3, h4, .title, a")
                date_el = item.query_selector("time, .date, [class*='date']")
                link_el = item.query_selector("a[href]")
                category_el = item.query_selector(".category, .tag, [class*='tag'], [class*='category']")

                if not title_el:
                    continue

                link = link_el.get_attribute("href") if link_el else ""
                if link and not link.startswith("http"):
                    link = BASE_URL + link

                articles.append({
                    "title": title_el.inner_text().strip(),
                    "date": date_el.inner_text().strip() if date_el else "",
                    "url": link,
                    "category": category_el.inner_text().strip() if category_el else "",
                })
            break  # stop at first selector that works

    return articles


def save_cache(articles):
    with open(CACHE_FILE, "w") as f:
        json.dump({"fetched_at": datetime.now().isoformat(), "articles": articles}, f, indent=2)
    print(f"Saved {len(articles)} articles to {CACHE_FILE}")


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    with open(CACHE_FILE) as f:
        data = json.load(f)
    print(f"Loaded cache from {data['fetched_at']} ({len(data['articles'])} articles)")
    return data["articles"]
