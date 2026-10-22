import json, re, feedparser
from datetime import date

def fetch_articles(source_name, feed_url):
    articles = []
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            # 安全获取简介，防止某些网站字段缺失导致崩溃
            summary = entry.get('summary', entry.get('description', 'No summary available'))[:300]
            
            articles.append({
                "id": len(articles) + 1,
                "cat": "world",
                "title": entry.title,
                "source": source_name,
                "date": str(date.today()),
                "img": "",
                "paras": [summary]
            })
    except Exception as e:
        print(f"Warning: Failed to fetch {source_name}: {e}")
    return articles

sources = [
    ("BBC", "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ("CNN", "http://rss.cnn.com/rss/edition.rss"),
    ("Reuters", "https://www.reutersagency.com/feed/?taxonomy=top-news&post_type=reuters-top-news")
]

all_articles = []
# 循环抓取，即使某一个源报错，也不影响其他源
for name, url in sources:
    all_articles.extend(fetch_articles(name, url))

# 重新分配全局ID
for i, art in enumerate(all_articles):
    art["id"] = i + 1

# 读取本地的 index.html 模板
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 替换数据
new_data = 'let ART=' + json.dumps(all_articles, ensure_ascii=False) + ';'
html = re.sub(r'let ART=\[.*?\];', new_data, html, flags=re.S)

# 写入新的 index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Successfully updated {len(all_articles)} articles.")
