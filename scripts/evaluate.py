"""Deterministic fixture evaluation. Precision=correct/predicted; recall=correct/expected."""
import json, time, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from app.extraction.content import collect_evidence
from app.services.validation import metadata_product
root=Path(__file__).parents[1]/"tests"/"fixtures"
rows=[]
for page in root.glob("*.html"):
    started=time.perf_counter(); product,_=metadata_product(collect_evidence(page.read_text(),"https://fixture.invalid/p")); rows.append({"fixture":page.name,"latency_ms":round((time.perf_counter()-started)*1000,2),"missing_fields":sum(v in (None,[],{}) for v in product.model_dump().values()),"product":product.model_dump()})
print(json.dumps({"fixtures":len(rows),"mean_latency_ms":sum(x['latency_ms'] for x in rows)/len(rows) if rows else 0,"results":rows,"note":"Mock/metadata-only evaluation; real LLM accuracy must be measured separately."},indent=2))
