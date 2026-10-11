from __future__ import annotations
from app.crawler.fetcher import fetch
from app.crawler.cloudflare import fetch_rendered
from app.extraction.content import collect_evidence
from app.extraction.prompt import build_prompt
from app.extraction.providers import GeminiProvider
from app.models.product import Product
from .validation import metadata_product, build_report
from .demo_budget import budget
async def extract_product(url: str, use_llm=True, fetch_mode="cloudflare"):
    if fetch_mode == "cloudflare":
        budget.consume()
        html, final_url, diagnostics=await fetch_rendered(url)
    elif fetch_mode == "local": html, final_url, diagnostics=await fetch(url)
    else: raise ValueError("fetch_mode must be 'cloudflare' or 'local'")
    evidence=collect_evidence(html,final_url)
    if not use_llm:
        product,report=metadata_product(evidence); report.diagnostics.update(diagnostics); return product,report
    provider=GeminiProvider(); status=await provider.status()
    if not status["configured"]: raise RuntimeError("Gemini is unavailable. Add GEMINI_API_KEY to .env, or choose metadata-only mode.")
    product=Product.model_validate(await provider.extract(build_prompt(url,final_url,evidence)))
    report=build_report(product,evidence); report.diagnostics.update(diagnostics); report.diagnostics["mode"]="gemini-api"; return product,report
