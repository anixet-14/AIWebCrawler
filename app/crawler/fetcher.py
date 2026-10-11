from __future__ import annotations
import os, httpx
from .safety import validate_url, URLSafetyError
from .robots import ensure_allowed

MAX_BYTES, MAX_REDIRECTS = 2_000_000, 5
class FetchError(RuntimeError): pass

async def fetch(url: str) -> tuple[str, str, dict]:
    url = validate_url(url); ua = os.getenv("UPC_USER_AGENT", "UniversalProductCrawler/0.1 (+local, respectful crawler)")
    timeout = httpx.Timeout(float(os.getenv("UPC_TIMEOUT_SECONDS", "15")))
    async with httpx.AsyncClient(headers={"User-Agent": ua, "Accept": "text/html,application/xhtml+xml"}, timeout=timeout, follow_redirects=False) as client:
        await ensure_allowed(url, ua, client)
        current = url
        for _ in range(MAX_REDIRECTS + 1):
            response = await client.get(current)
            if response.is_redirect:
                target = response.headers.get("location")
                if not target: raise FetchError("redirect without location")
                current = validate_url(str(response.url.join(target))); continue
            if response.status_code in {401, 403, 429}: raise FetchError(f"site denied automated access (HTTP {response.status_code})")
            response.raise_for_status()
            if int(response.headers.get("content-length", "0") or 0) > MAX_BYTES: raise FetchError("response exceeds size limit")
            body = response.content
            if len(body) > MAX_BYTES: raise FetchError("response exceeds size limit")
            return body.decode(response.encoding or "utf-8", errors="replace"), current, {"status_code": response.status_code, "rendered": False}
        raise FetchError("too many redirects")
