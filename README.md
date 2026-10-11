# Universal AI Product Crawler

A demo-minded prototype that extracts the required ten-field product JSON without retailer-specific selectors. Cloudflare Browser Run fetches pages remotely, then Gemini 3.8 Flash interprets only the bounded returned evidence and produces schema-constrained JSON.

## Windows PowerShell quick start

```powershell
cd C:\path\to\universal-product-crawler
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
# another terminal
streamlit run app/ui/streamlit_app.py
pytest -q
python scripts/evaluate.py
```

The tests and metadata-only mode need no model. For semantic extraction, create a Gemini API key in Google AI Studio and set `GEMINI_API_KEY` in `.env`. The default `GEMINI_MODEL=gemini-3.8-flash` can be changed without code. The app does not use Gemini browsing or grounding: Cloudflare fetches the page first, and only the resulting evidence is sent to Gemini.

## Cloudflare demo setup

Copy `.env.example` to `.env`, then replace `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, and `GEMINI_API_KEY`. The Cloudflare token needs the narrow `Browser Run - Edit` permission. Do not share or commit `.env`. The default remote limit is five requests per server process/day; alter `UPC_REMOTE_DAILY_LIMIT` only while remaining inside Cloudflare's free allowance. Remote mode makes a single Cloudflare Browser Run `/content` request, with media/fonts/images blocked, and does not rotate IPs, solve CAPTCHAs, or attempt to bypass access controls. Select **Cloudflare remote browser** in the UI (or omit `fetch_mode` from the API request).

Example:
```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/extract -Method Post -ContentType application/json -Body '{"url":"https://example.com/product","use_llm":false,"debug":true}'
```

Endpoints: `GET /health`, `GET /api/config`, `POST /api/validate`, and `POST /api/extract`. The extract endpoint returns `product`; `debug:true` separately adds field evidence, confidence, warnings, and diagnostics.

## Safety and limitations

Only crawl public HTTP(S) URLs you are permitted to access. The service rejects local/private destinations, re-checks redirects, honors reachable `robots.txt`, has time/size/redirect limits, and reports bot blocks rather than bypassing them. It does not log in, solve CAPTCHAs, use proxies, or scrape personal data. Metadata-only mode has lower coverage; local LLM extraction can still make errors and always requires schema validation and review for consequential use.

Optional JS rendering is implemented but deliberately not automatic: use only where browser automation is allowed, after `playwright install`. See `docs/` for architecture, cost, and failure modes.
