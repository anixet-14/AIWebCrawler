"""Optional, deliberately opt-in browser fallback; no login or interaction."""
from .fetcher import FetchError
async def render(url: str) -> str:
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc: raise FetchError("Playwright is unavailable; install it and run playwright install") from exc
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.route("**/*", lambda route: route.abort() if route.request.resource_type in {"image","media","font"} else route.continue_())
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            return await page.content()
        finally: await browser.close()
