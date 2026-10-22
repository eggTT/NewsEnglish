import json, requests, feedparser
from datetime import date

def fetch_articles(source_name, feed_url):
    articles = []
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            articles.append({
                "id": len(articles) + 1,
                "cat": "world",
                "title": entry.title,
                "source": source_name,
                "date": str(date.today()),
                "img": "",
                "paras": [entry.get("summary", entry.description)[:300]]
            })
    except Exception as e:
        print(f"Error fetching {source_name}: {e}")
    return articles

sources = [
    ("BBC", "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ("CNN", "http://rss.cnn.com/rss/edition.rss"),
    ("Reuters", "https://www.reutersagency.com/feed/?taxonomy=top-news&post_type=reuters-top-news")
]

all_articles = []
for name, url in sources:
    all_articles.extend(fetch_articles(name, url))

for i, art in enumerate(all_articles):
    art["id"] = i + 1

with open("NewsEnglish.html", "r", encoding="utf-8") as f:
    html = f.read()

import re
html = re.sub(r'let ART=\[.*?\];', 'let ART=' + json.dumps(all_articles, ensure_ascii=False) + ';', html, flags=re.S)

with open("NewsEnglish.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Successfully updated {len(all_articles)} articles.")
