import json
import requests
import feedparser
from datetime import date
import re

def fetch_articles(source_name, feed_url):
    articles = []
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            # 加上容错处理，防止因为某个字段缺失导致崩溃
            summary = ""
            if hasattr(entry, 'description'):
                summary = entry.description
            elif hasattr(entry, 'summary'):
                summary = entry.summary
            
            articles.append({
                "id": len(articles) + 1,
                "cat": "world",
                "title": entry.title,
                "source": source_name,
                "date": str(date.today()),
                "img": "",
                "paras": [summary[:300]] if summary else ["No summary available."]
            })
    except Exception as e:
        # 打印错误但不崩溃，保证后续代码能继续执行
        print(f"Error fetching {source_name}: {e}")
    return articles

sources = [
    ("BBC", "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ("CNN", "http://rss.cnn.com/rss/edition.rss"),
    ("Reuters", "https://www.reutersagency.com/feed/?taxonomy=top-news&post_type=reuters-top-news")
]

all_articles = []
for name, url in sources:
    # 确保循环不会因为单个网站报错而彻底停止
    try:
        all_articles.extend(fetch_articles(name, url))
    except Exception as e:
        print(f"Skipped {name} due to error: {e}")

# 重新分配 ID
for i, art in enumerate(all_articles):
    art["id"] = i + 1

# 检查 index.html 是否存在
html = ""
try:
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
except FileNotFoundError:
    print("Warning: index.html not found in the repository! Skipping update.")
    exit(0)

# 替换掉旧的 let ART=[...]
new_data = 'let ART=' + json.dumps(all_articles, ensure_ascii=False) + ';'
if re.search(r'let ART=\[.*?\];', html, flags=re.S):
    html = re.sub(r'let ART=\[.*?\];', new_data, html, flags=re.S)
else:
    # 如果找不到 let ART，就在 </head> 或 </body> 前插入（兜底方案）
    html = html.replace("</head>", f"{new_data}</head>")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Successfully updated {len(all_articles)} articles in index.html.")
