"""Compliant remote rendering through Cloudflare Browser Run.

This is not a proxy pool: one bounded Browser Run Quick Action is made per user
request. It must not be used to bypass access controls, CAPTCHAs, or robots.
"""
from __future__ import annotations
import os
from urllib.parse import urlsplit, urlunsplit
import httpx

class RemoteFetchError(RuntimeError): pass

def validate_remote_url(raw: str) -> str:
    """Syntax-only validation avoids a direct local DNS lookup of the target."""
    p = urlsplit(raw.strip())
    if p.scheme not in {"http", "https"} or not p.hostname or p.username or p.password:
        raise RemoteFetchError("URL must be a public HTTP(S) URL without credentials")
    host = p.hostname.rstrip(".").lower()
    blocked = {"localhost", "localhost.localdomain", "0.0.0.0", "127.0.0.1", "::1"}
    if host in blocked or host.endswith(".local"):
        raise RemoteFetchError("local destinations are not permitted")
    return urlunsplit((p.scheme, p.netloc, p.path or "/", p.query, ""))

def configured() -> bool:
    values = (os.getenv("CLOUDFLARE_ACCOUNT_ID", ""), os.getenv("CLOUDFLARE_API_TOKEN", ""))
    return all(values) and not any(value.startswith("replace_") for value in values)

async def fetch_rendered(url: str) -> tuple[str, str, dict]:
    url = validate_remote_url(url)
    account_id, token = os.getenv("CLOUDFLARE_ACCOUNT_ID"), os.getenv("CLOUDFLARE_API_TOKEN")
    if not configured():
        raise RemoteFetchError("Cloudflare Browser Run is not configured. Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in .env.")
    endpoint = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/browser-run/content"
    payload = {"url": url, "rejectResourceTypes": ["image", "media", "font"], "gotoOptions": {"waitUntil": "domcontentloaded", "timeout": 20000}}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(endpoint, json=payload, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        if response.status_code in {401, 403}: raise RemoteFetchError("Cloudflare denied the API token; verify Browser Run - Edit permission.")
        if response.status_code == 429: raise RemoteFetchError("Cloudflare Browser Run quota/rate limit reached. Try again tomorrow or reduce demo usage.")
        response.raise_for_status(); envelope = response.json()
        if not envelope.get("success") or not isinstance(envelope.get("result"), str):
            raise RemoteFetchError(envelope.get("errors", [{"message": "Cloudflare returned no rendered HTML"}])[0].get("message", "Cloudflare request failed"))
        return envelope["result"], url, {"fetch_provider": "cloudflare-browser-run", "rendered": True, "browser_ms_used": response.headers.get("X-Browser-Ms-Used")}
    except httpx.HTTPError as exc:
        raise RemoteFetchError(f"Cloudflare Browser Run request failed: {exc}") from exc
