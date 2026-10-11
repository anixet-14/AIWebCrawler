from __future__ import annotations
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def _texts(value):
    if isinstance(value, list): return " ".join(map(str, value))
    return str(value) if value is not None else ""

def collect_evidence(html: str, page_url: str) -> dict:
    """Generic standards-based extraction; classes and IDs are never consulted."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "template", "svg"]):
        if tag.name != "script" or tag.get("type") == "application/ld+json": continue
        tag.decompose()
    metadata = {}
    for tag in soup.find_all("meta"):
        key = tag.get("property") or tag.get("name") or tag.get("itemprop")
        value = tag.get("content")
        if key and value: metadata[key.lower()] = value.strip()
    structured = []
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(tag.string or tag.get_text())
            structured.append(data)
        except (json.JSONDecodeError, TypeError): pass
    images = []
    for key in ("og:image", "twitter:image", "image"):
        if metadata.get(key): images.append(urljoin(page_url, metadata[key]))
    for tag in soup.find_all("img"):
        source = tag.get("src") or tag.get("data-src")
        if source: images.append(urljoin(page_url, source))
    headings = [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"])][:20]
    text = soup.get_text(" ", strip=True)
    return {"page_url": page_url, "title": soup.title.get_text(" ", strip=True) if soup.title else "", "metadata": metadata,
            "structured_data": structured, "headings": headings, "visible_text": text[:30000],
            "images": list(dict.fromkeys(images))[:30]}
