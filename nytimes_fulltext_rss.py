import requests
import feedgenerator
import feedparser
import trafilatura
from datetime import datetime
import time
import sys

RSS_URL = "https://cn.nytimes.com/rss/news.xml"   # 纽约时报中文官方 RSS
OUTPUT_FILE = "feed.xml"
USER_AGENT = "Mozilla/5.0 (compatible; KindleEar-NYT-RSS/1.0)"

def clean_html(html):
    if not html:
        return ""
    # 清理 NYT 常见多余元素
    import re
    html = re.sub(r'<div class="[^"]*?(ad|related|share|footer|header|nav)[^"]*?".*?</div>', '', html, flags=re.I | re.S)
    return html

def fetch_fulltext(url):
    try:
        downloaded = trafilatura.fetch_url(url, decode=True)
        if downloaded:
            result = trafilatura.extract(downloaded, 
                                       include_formatting=True,
                                       include_links=True,
                                       include_images=True,
                                       output_format="html",
                                       favor_recall=True)
            return clean_html(result) if result else None
    except Exception as e:
        print(f"提取失败 {url}: {e}")
    return None

def main():
    print("开始获取 NYT 中文 RSS...")

    feed = feedgenerator.Rss201rev2Feed(
        title="纽约时报中文网 - 全文版",
        link="https://cn.nytimes.com/",
        description="纽约时报中文网全文 RSS（GitHub Actions 生成）",
        language="zh-CN",
    )

    resp = requests.get(RSS_URL, headers={"User-Agent": USER_AGENT}, timeout=30)
    original_feed = feedparser.parse(resp.content)

    print(f"共发现 {len(original_feed.entries)} 条新闻")

    for i, entry in enumerate(original_feed.entries[:20]):
        title = entry.get('title', '无标题')
        link = entry.get('link')
        print(f"[{i+1}/20] 处理: {title[:60]}...")

        full_content = fetch_fulltext(link)
        description = full_content if full_content else entry.get('summary', entry.get('description', ''))

        pub_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
        pubdate = datetime(*pub_parsed[:6]) if pub_parsed else datetime.utcnow()

        feed.add_item(
            title=title,
            link=link,
            description=description,
            pubdate=pubdate,
            unique_id=link,
        )
        time.sleep(2)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        feed.write(f, 'utf-8')

    print("✅ NYT 中文全文 RSS 生成完成")

if __name__ == "__main__":
    main()
