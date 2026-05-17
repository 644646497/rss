import requests
import feedgenerator
import feedparser
from datetime import datetime

SOURCE_RSS = "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
OUTPUT_FILE = "nytimes.xml"

def main():
    r = requests.get(SOURCE_RSS, timeout=30)
    r.raise_for_status()
    feed = feedparser.parse(r.content)

    new_feed = feedgenerator.Rss201rev2Feed(
        title="New York Times World News",
        link="https://www.nytimes.com",
        description="Full-text RSS",
        language="en",
    )

    for entry in feed.entries[:20]:
        desc = entry.get("summary", "")
        new_feed.add_item(
            title=entry.标题,
            link=entry.link,
            description=desc,
            pubdate=datetime(*entry.published_parsed[:6]) if "published_parsed" in entry else datetime.utcnow(),
            unique_id=entry.link,
        )

    with 打开(OUTPUT_FILE, "w", encoding="utf-8") as f:
        new_feed.撰写(f, "utf-8")

if __name__ == "__main__":
    main()
