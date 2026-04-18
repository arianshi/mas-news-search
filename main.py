#!/usr/bin/env python3
"""
MAS News Search — fetch and search Singapore MAS news articles.

Usage:
  python main.py fetch                        # fetch latest news (all categories)
  python main.py fetch --category speeches    # fetch a specific category
  python main.py fetch --pages 3              # fetch multiple pages
  python main.py search "interest rate"       # search cached articles
  python main.py search "fintech" --limit 5   # limit results
"""

import argparse
from scraper import fetch_news, save_cache, load_cache, NEWS_CATEGORIES
from search import search, display


def cmd_fetch(args):
    articles = fetch_news(category=args.category, pages=args.pages)
    if articles:
        save_cache(articles)
        display(articles[:10])
    else:
        print("No articles fetched. The MAS website may be unavailable.")


def cmd_search(args):
    articles = load_cache()
    if articles is None:
        print("No cache found. Run 'python main.py fetch' first.")
        return

    results = search(articles, keyword=args.keyword, category=args.category, limit=args.limit)
    display(results)


def main():
    parser = argparse.ArgumentParser(description="Search Singapore MAS news")
    sub = parser.add_subparsers(dest="command")

    # fetch command
    fetch_parser = sub.add_parser("fetch", help="Fetch latest news from MAS website")
    fetch_parser.add_argument(
        "--category",
        choices=list(NEWS_CATEGORIES.keys()),
        default="all",
        help="News category to fetch (default: all)",
    )
    fetch_parser.add_argument(
        "--pages", type=int, default=1, help="Number of pages to fetch (default: 1)"
    )

    # search command
    search_parser = sub.add_parser("search", help="Search cached articles")
    search_parser.add_argument("keyword", nargs="?", help="Keyword to search for")
    search_parser.add_argument("--category", help="Filter by category")
    search_parser.add_argument(
        "--limit", type=int, default=20, help="Max results to show (default: 20)"
    )

    args = parser.parse_args()

    if args.command == "fetch":
        cmd_fetch(args)
    elif args.command == "search":
        cmd_search(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
