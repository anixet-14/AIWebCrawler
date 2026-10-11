from __future__ import annotations
import json, re
from urllib.parse import urljoin
from app.models.product import Product, ExtractionReport, FieldEvidence
def _find_product(data):
    if isinstance(data, list):
        for x in data:
            found=_find_product(x)
            if found:return found
    if isinstance(data, dict):
        types=data.get("@type",[]); types=[types] if isinstance(types,str) else types
        if "Product" in types:return data
        for x in data.get("@graph",[]):
            found=_find_product(x)
            if found:return found
    return None
def metadata_product(evidence: dict) -> tuple[Product, ExtractionReport]:
    """Explicitly labelled lower-coverage fallback, never guessing absent values."""
    m=evidence["metadata"]; structured=next((x for x in (_find_product(x) for x in evidence["structured_data"]) if x), {})
    offer=structured.get("offers", {}) if isinstance(structured,dict) else {}; offer=offer[0] if isinstance(offer,list) and offer else offer
    brand=structured.get("brand"); brand=brand.get("name") if isinstance(brand,dict) else brand
    rating=structured.get("aggregateRating", {}) or {}
    raw_images=structured.get("image") or evidence["images"]
    if isinstance(raw_images, str): raw_images=[raw_images]
    images=[urljoin(evidence.get("page_url", ""), x) for x in raw_images or []]
    properties=structured.get("additionalProperty", []) or []
    if isinstance(properties, dict): properties=[properties]
    specs={str(x.get("name", "")).strip(): str(x.get("value", "")).strip() for x in properties if isinstance(x,dict) and x.get("name") and x.get("value") is not None}
    raw={"name":structured.get("name") or m.get("og:title"),"brand":brand,"price":offer.get("price"),"currency":offer.get("priceCurrency"),"availability":offer.get("availability"),"images":images,"rating":rating.get("ratingValue"),"review_count":rating.get("reviewCount"),"description":structured.get("description") or m.get("og:description"),"specs":specs}
    product=Product.model_validate(raw); report=build_report(product,evidence); report.diagnostics["mode"]="metadata-only"; return product,report
def build_report(product: Product, evidence: dict) -> ExtractionReport:
    report=ExtractionReport(); serialized=product.model_dump()
    blob=json.dumps({"metadata":evidence.get("metadata",{}),"structured_data":evidence.get("structured_data",[])},default=str)
    for field,value in serialized.items():
        if value in (None, [], {}): report.missing_fields.append(field); report.confidence[field]="missing"; continue
        source="structured/metadata" if field.lower() in blob.lower() else "LLM interpreted evidence"
        report.evidence[field]=[FieldEvidence(source=source,excerpt=str(value)[:180])]; report.confidence[field]="strong" if source.startswith("structured") else "moderate"
    visible=evidence.get("visible_text","")
    if product.price is not None and str(product.price) not in visible: report.conflicts.append("price is not corroborated in visible text")
    return report
