import os
from datetime import datetime
from email.utils import formatdate

FEED_TITLE = "General Conference Audio"
FEED_DESCRIPTION = "Audio recordings from The Church of Jesus Christ of Latter-day Saints General Conferences."
FEED_LINK = "https://www.churchofjesuschrist.org/study/general-conference?lang=eng"
FEED_LANG = "en"
FEED_AUTHOR = "The Church of Jesus Christ of Latter-day Saints"
FEED_SELF_LINK = os.environ.get("FEED_SELF_LINK", "https://davidcstevens.github.io/general-conference-feed/feed.xml")
ITUNES_IMAGE = os.environ.get("ITUNES_IMAGE", "")

RSS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
  xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{title}</title>
    <description>{description}</description>
    <link>{link}</link>
    <language>{lang}</language>
    <atom:link href="{self_link}" rel="self" type="application/rss+xml" />
    <lastBuildDate>{build_date}</lastBuildDate>
    <generator>conference-feed</generator>
    <itunes:author>{author}</itunes:author>
    <itunes:summary>{description}</itunes:summary>
    <itunes:explicit>no</itunes:explicit>
    {itunes_image}
    {items}
  </channel>
</rss>
"""

ITEM_TEMPLATE = """    <item>
      <title><![CDATA[{title}]]></title>
      <description><![CDATA[{description}]]></description>
      <link>{source_url}</link>
      <guid isPermaLink="false">{guid}</guid>
      <pubDate>{pubdate}</pubDate>
      <enclosure url="{mp3}" type="audio/mpeg" length="{length}" />
      <itunes:duration>{duration}</itunes:duration>
      <itunes:author>{author}</itunes:author>
    </item>
"""

def build_feed(episodes, out_path="feed.xml"):
    items_xml = []
    for ep in episodes:
        pub = ep["pubdate"]
        pubdate = formatdate(pub.timestamp()) if hasattr(pub, "timestamp") else formatdate()
        items_xml.append(ITEM_TEMPLATE.format(
            title=ep["title"],
            description=f"General Conference session: {ep['title']}",
            source_url=ep["url"],
            guid=ep["guid"],
            pubdate=pubdate,
            mp3=ep["mp3"],
            length=ep.get("length", 0),
            duration=ep.get("duration", ""),
            author=FEED_AUTHOR,
        ))
    itunes_image_xml = ""
    if ITUNES_IMAGE:
        itunes_image_xml = f'<itunes:image href="{ITUNES_IMAGE}" />'
    rss = RSS_TEMPLATE.format(
        title=FEED_TITLE,
        description=FEED_DESCRIPTION,
        link=FEED_LINK,
        lang=FEED_LANG,
        self_link=FEED_SELF_LINK,
        build_date=formatdate(),
        author=FEED_AUTHOR,
        itunes_image=itunes_image_xml,
        items="\n".join(items_xml),
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(rss)
    print(f"Wrote {out_path} with {len(episodes)} episodes")
