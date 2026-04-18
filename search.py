def search(articles, keyword=None, category=None, limit=20):
    """Filter articles by keyword and/or category."""
    results = articles

    if keyword:
        kw = keyword.lower()
        results = [
            a for a in results
            if kw in a["title"].lower() or kw in a.get("category", "").lower()
        ]

    if category:
        cat = category.lower()
        results = [a for a in results if cat in a.get("category", "").lower()]

    return results[:limit]


def display(articles):
    """Print articles in a readable format."""
    if not articles:
        print("No results found.")
        return

    print(f"\n{'─' * 70}")
    for i, article in enumerate(articles, 1):
        date = f"[{article['date']}] " if article["date"] else ""
        category = f"  ({article['category']})" if article["category"] else ""
        print(f"{i:>3}. {date}{article['title']}{category}")
        if article["url"]:
            print(f"      {article['url']}")
        print()
    print(f"{'─' * 70}")
    print(f"Total: {len(articles)} result(s)")
