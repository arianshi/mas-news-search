from flask import Flask, jsonify, render_template, request
from scraper import fetch_news, save_cache, load_cache, NEWS_CATEGORIES
import urllib.request, ssl, certifi
import xml.etree.ElementTree as ET
import re

_ssl_ctx = ssl.create_default_context(cafile=certifi.where())

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/articles")
def api_articles():
    import json, os
    cache_file = os.path.join(os.path.dirname(__file__), "news_cache.json")
    if not os.path.exists(cache_file):
        return jsonify({"articles": [], "fetched_at": None})
    with open(cache_file) as f:
        return jsonify(json.load(f))


@app.route("/api/fetch", methods=["POST"])
def api_fetch():
    category = request.args.get("category", "all")
    if category not in NEWS_CATEGORIES:
        category = "all"

    articles = fetch_news(category=category, pages=1)
    if not articles:
        return jsonify({"error": "MAS website is currently under maintenance. Please try again later."}), 503

    save_cache(articles)
    return jsonify({"count": len(articles)})


@app.route("/api/search")
def api_search():
    from search import search
    articles = load_cache()
    if articles is None:
        return jsonify({"articles": []})
    keyword = request.args.get("q", "")
    category = request.args.get("category", "")
    results = search(articles, keyword=keyword or None, category=category or None)
    return jsonify({"articles": results, "total": len(results)})


@app.route("/api/latest")
def api_latest():
    rss_url = "https://news.google.com/rss/search?q=MAS+Singapore+monetary+authority&hl=en-SG&gl=SG&ceid=SG:en"
    try:
        req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        items = []
        for item in root.findall("./channel/item"):
            title = item.findtext("title", "").strip()
            link  = item.findtext("link", "").strip()
            pub   = item.findtext("pubDate", "").strip()
            desc  = item.findtext("description", "")
            # Extract source name from description HTML
            source_match = re.search(r'<font[^>]*>([^<]+)</font>', desc)
            source = source_match.group(1) if source_match else ""
            items.append({"title": title, "url": link, "date": pub, "source": source})
        return jsonify({"articles": items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5050, debug=False)
