import json, re, feedparser
from datetime import date
from html import unescape

def clean_html(raw_html):
    """清理HTML标签，提取纯文本段落"""
    # 移除 script 和 style 标签
    raw_html = re.sub(r'<script.*?>.*?</script>', '', raw_html, flags=re.S|re.I)
    raw_html = re.sub(r'<style.*?>.*?</style>', '', raw_html, flags=re.S|re.I)
    # 将 <br> 和 </p> 替换为换行
    raw_html = re.sub(r'<br\s*/?>', '\n', raw_html)
    raw_html = re.sub(r'</p>', '\n\n', raw_html)
    # 移除所有剩余的HTML标签
    text = re.sub(r'<.*?>', '', raw_html)
    # 解码HTML实体（如 &amp; -> &）
    text = unescape(text)
    # 按换行符分割成段落，过滤掉空行
    paras = [p.strip() for p in text.split('\n') if p.strip()]
    return paras

def get_first_image(raw_html):
    """提取HTML中的第一张图片URL"""
    match = re.search(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', raw_html)
    if match:
        return match.group(1)
    return "https://via.placeholder.com/600x400?text=No+Image" # 无图时的占位图

def fetch_articles(source_name, feed_url):
    articles = []
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            # 优先获取 content，如果没有则获取 summary
            raw_content = entry.get('content', [{}])[0].get('value', '') if 'content' in entry else entry.get('summary', '')
            
            if not raw_content:
                continue
                
            # 提取正文（分段）
            paras = clean_html(raw_content)
            # 提取配图
            img_url = get_first_image(raw_content)
            
            articles.append({
                "id": len(articles) + 1,
                "cat": "world",
                "title": unescape(entry.title),
                "source": source_name,
                "date": str(date.today()),
                "img": img_url,
                "paras": paras[:10] # 限制最多显示10段，防止页面过长
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
for name, url in sources:
    all_articles.extend(fetch_articles(name, url))

for i, art in enumerate(all_articles):
    art["id"] = i + 1

# 读取 index.html 模板
try:
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
except FileNotFoundError:
    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>News</title></head>
<body><div id="app"></div><script>let ART=[];</script></body></html>"""

# 替换数据
new_data = 'let ART=' + json.dumps(all_articles, ensure_ascii=False) + ';'
html = re.sub(r'let ART=\[.*?\];', new_data, html, flags=re.S)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Successfully updated {len(all_articles)} articles with images.")
