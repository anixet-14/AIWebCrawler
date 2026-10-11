from pathlib import Path
import json
PROMPT_PATH = Path(__file__).parents[2] / "prompts" / "product_extraction.txt"
def build_prompt(url: str, final_url: str, evidence: dict) -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    # A 3B local model is more reliable with focused, bounded evidence.
    metadata = {k: str(v)[:400] for k, v in list(evidence.get("metadata", {}).items())[:60]}
    structured = json.dumps(evidence.get("structured_data", []), ensure_ascii=False)[:8000]
    focused = {"title": evidence.get("title", "")[:500], "metadata": metadata,
               "structured_data_json": structured, "headings": evidence.get("headings", [])[:20],
               "visible_text": evidence.get("visible_text", "")[:12000], "images": evidence.get("images", [])[:15]}
    return template.replace("{{url}}", url).replace("{{final_url}}", final_url).replace("{{evidence}}", json.dumps(focused, ensure_ascii=False))
