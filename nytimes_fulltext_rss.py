import requests
import feedparser
import trafilatura
from datetime import datetime
import time
import re

# 改用官方中文源
RSS_URL = "https://feedx.net/rss/nytimes.xml"
OUTPUT_FILE = "feed.xml"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def fetch_fulltext(url):
    """抓取纽约时报中文网全文"""
    try:
        # 直接请求文章页面
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            return None
        
        # 使用 trafilatura 提取正文
        result = trafilatura.extract(resp.text, include_formatting=True)
        if result:
            # 清理多余空白
            result = re.sub(r'\n\s*\n', '\n\n', result)
            return result
    except Exception as e:
        print(f"  全文提取失败: {e}")
    return None

def main():
    print("开始抓取纽约时报中文网全文...")
    
    # 获取 RSS 列表
    resp = requests.get(RSS_URL, headers=HEADERS, timeout=30)
    print(f"RSS 状态码: {resp.status_code}")
    
    feed = feedparser.parse(resp.content)
    print(f"找到 {len(feed.entries)} 篇文章")
    
    rss_items = []
    
    for i, entry in enumerate(feed.entries[:10]):
        title = entry.get('title', '无标题')
        link = entry.get('link')
        if not link:
            continue
        
        print(f"[{i+1}] 抓取: {title[:40]}...")
        
        # 提取全文
        content = fetch_fulltext(link)
        if not content:
            content = entry.get('summary', entry.get('description', '无法提取全文'))
            print(f"  使用摘要")
        else:
            print(f"  成功提取全文 ({len(content)} 字符)")
        
        pubdate = entry.get('published_parsed')
        if pubdate:
            pubdate = datetime(*pubdate[:6])
        else:
            pubdate = datetime.now()
        
        rss_items.append({
            'title': title,
            'link': link,
            'description': content,
            'pubdate': pubdate
        })
        
        time.sleep(1)  # 避免请求过快
    
    # 生成 RSS
    rss_output = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>纽约时报中文 - 全文版</title>
<link>https://cn.nytimes.com/</link>
<description>自动抓取的纽约时报中文全文</description>
<lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
'''
    
    for item in rss_items:
        # 清理 description 中的特殊字符
        desc = item['description']
        if desc:
            desc = desc.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        rss_output += f'''
<item>
    <title><![CDATA[{item['title']}]]></title>
    <link>{item['link']}</link>
    <pubDate>{item['pubdate'].strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
    <description><![CDATA[
        <h2>{item['title']}</h2>
        <hr/>
        {item['description']}
        <hr/>
        <p><a href="{item['link']}">📖 阅读原文</a></p>
    ]]></description>
</item>'''
    
    rss_output += '\n</channel>\n</rss>'
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(rss_output)
    
    print(f"\n✅ 完成！共 {len(rss_items)} 篇文章")

if __name__ == "__main__":
    main()
