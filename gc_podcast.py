import os
import re
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

GC_BASE = "https://www.churchofjesuschrist.org"
GC_LANDING = f"{GC_BASE}/study/general-conference?lang=eng"

HEADERS = {
    "User-Agent": "GeneralConferencePodcastFeed/1.0 (+https://github.com/viduno/conference-feed)"
}

DOWNLOAD_SELECTORS = [
    "a.downloadLink-Bzfm4",
    "a[data-testid*='download-link']",
    "a[download][href$='.mp3']",
    "a[href$='.mp3']",
]

def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def find_mp3_links(page_html, base_url):
    soup = BeautifulSoup(page_html, "lxml")
    seen = set()
    out = []
    for sel in DOWNLOAD_SELECTORS:
        for a in soup.select(sel):
            href = a.get("href")
            if href and href.endswith(".mp3"):
                mp3 = urljoin(base_url, href)
                if mp3 not in seen:
                    seen.add(mp3)
                    out.append(mp3)
    if out:
        return out
    for m in re.findall(r'https?://[^\s"\'<>()]+\.mp3[^\s"\'<>()]*', page_html):
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out

def extract_title(soup, page_url):
    for tag in ["h1", "title"]:
        t = soup.select_one(tag)
        if t and t.get_text(strip=True):
            txt = t.get_text(strip=True)
            txt = re.sub(r"\s*\|\s*Church of Jesus Christ.*$", "", txt)
            return txt
    return os.path.basename(urlparse(page_url).path) or "General Conference Session"

def extract_pubdate(soup, page_url):
    m = soup.find("meta", property="article:published_time") or soup.find("meta", itemprop="datePublished")
    if m and m.get("content"):
        try:
            return dateparser.isoparse(m["content"]).replace(tzinfo=None)
        except Exception:
            pass
    text = soup.get_text(" ", strip=True)
    mm = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', text)
    if mm:
        try:
            return dateparser.parse(mm.group(0)).replace(tzinfo=None)
        except Exception:
            pass
    return datetime.utcnow()

def discover_conference_urls():
    html = fetch(GC_LANDING)
    soup = BeautifulSoup(html, "lxml")
    urls = set()
    for a in soup.select("a[href*='/study/general-conference/']"):
        href = a.get("href")
        if not href:
            continue
        full = urljoin(GC_BASE, href)
        if "lang=eng" not in full:
            full = full + ("&" if "?" in full else "?") + "lang=eng"
        if re.search(r"/general-conference/\d{4}/(04|10)", full):
            urls.add(full)
    return sorted(urls)

def collect_episodes(max_confs=6):
    conf_urls = discover_conference_urls()
    def key(u):
        m = re.search(r"/(\d{4})/(04|10)", u)
        return (int(m.group(1)) if m else 0, int(m.group(2)) if m else 0)
    conf_urls.sort(key=key, reverse=True)
    conf_urls = conf_urls[:max_confs*10]

    episodes = []
    seen_mp3 = set()
    for page in conf_urls:
        try:
            html = fetch(page)
        except Exception as e:
            print(f"Warn: failed to fetch {page}: {e}", file=sys.stderr)
            continue
        soup = BeautifulSoup(html, "lxml")
        mp3s = find_mp3_links(html, page)
        if not mp3s:
            continue
        title = extract_title(soup, page)
        pub = extract_pubdate(soup, page)
        for i, mp3 in enumerate(mp3s):
            if mp3 in seen_mp3:
                continue
            seen_mp3.add(mp3)
            ep_title = title
            if len(mp3s) > 1:
                ep_title = f"{title} (Part {i+1})"
            episodes.append({
                "title": ep_title,
                "url": page,
                "mp3": mp3,
                "pubdate": pub,
                "guid": mp3,
            })
    episodes.sort(key=lambda e: (e["pubdate"], e["title"]), reverse=True)
    return episodes
