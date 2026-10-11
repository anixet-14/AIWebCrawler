from __future__ import annotations
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
import httpx

class RobotsError(PermissionError): pass

async def ensure_allowed(url: str, user_agent: str, client: httpx.AsyncClient) -> None:
    p = urlsplit(url); robots_url = f"{p.scheme}://{p.netloc}/robots.txt"
    try:
        response = await client.get(robots_url, follow_redirects=False)
        if response.status_code >= 400: return  # unavailable robots is not an inferred prohibition
        parser = RobotFileParser(); parser.parse(response.text.splitlines())
        if not parser.can_fetch(user_agent, url): raise RobotsError("robots.txt disallows this URL for the configured user agent")
    except httpx.HTTPError:
        return  # network failure is reported by the page fetch; do not pretend policy was known
