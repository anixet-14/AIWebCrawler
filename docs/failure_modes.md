# What breaks first

| Issue | Symptom/detection | Mitigation and remaining limit |
|---|---|---|
| CAPTCHA, anti-bot, authentication | 401/403/challenge page | Report failure; never bypass it. |
| robots/access terms | robots disallow or policy uncertainty | Stop when disallowed; review terms. |
| JavaScript content | sparse initial evidence | Optional bounded Playwright; some pages remain inaccessible. |
| Misleading/missing metadata | conflicts or null fields | Preserve evidence/conflicts; do not guess. |
| Currency, variants, regional pricing | multiple prices/ambiguous offer | Leave values null unless evidence identifies current product. |
| Async reviews/images | absent/de-duplicated candidates | Render only when permitted; results can remain incomplete. |
| LLM JSON/hallucination | parse/schema/evidence mismatch | Strict validation, bounded provider failures, manual review. |
| Local resources | timeout/Ollama unavailable | Metadata-only mode; choose smaller model/hardware. |
| Network/rate limits | timeout/429 | Bounded requests, respect limits, retry only transient cases. |
| Generalization changes | poorer fixture/live metrics | Monitor representative permitted pages; no site-specific workaround. |
