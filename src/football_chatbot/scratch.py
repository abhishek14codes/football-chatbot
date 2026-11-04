from football_chatbot.queries import get_article, search_articles

results = search_articles(["high line", "defensive line"], team="Barcelona", limit=2)
for r in results:
    print(r["title"], "|", len(r["excerpt"].split()), "words in excerpt")

article = get_article(results[0]["url"])
print("\n", article["title"], "| truncated:", article["truncated"])
print(article["body"][:800])