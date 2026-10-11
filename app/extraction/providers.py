from __future__ import annotations
import os, json, asyncio, httpx
from google import genai
from abc import ABC, abstractmethod
class LLMError(RuntimeError): pass
class Provider(ABC):
    @abstractmethod
    async def extract(self, prompt: str) -> dict: ...
class OllamaProvider(Provider):
    def __init__(self, base_url=None, model=None): self.base_url=(base_url or os.getenv("UPC_OLLAMA_URL", "http://127.0.0.1:11434")).rstrip("/"); self.model=model or os.getenv("UPC_OLLAMA_MODEL", "qwen2.5:3b-instruct")
    async def status(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=3) as c:
                r=await c.get(f"{self.base_url}/api/tags"); r.raise_for_status(); names=[m.get("name") for m in r.json().get("models", [])]
                return {"reachable": True, "model": self.model, "available": self.model in names}
        except httpx.HTTPError: return {"reachable": False, "model": self.model, "available": False}
    async def extract(self, prompt: str) -> dict:
        payload={"model":self.model,"prompt":prompt,"stream":False,"format":"json","options":{"temperature":0}}
        try:
            async with httpx.AsyncClient(timeout=90) as c:
                r=await c.post(f"{self.base_url}/api/generate",json=payload)
                if r.is_error:
                    raise LLMError(f"Ollama returned HTTP {r.status_code}: {r.text[:500]}")
                return json.loads(r.json()["response"])
        except LLMError: raise
        except (httpx.HTTPError, KeyError, json.JSONDecodeError) as exc: raise LLMError(f"local Ollama extraction failed: {exc}") from exc
class MockProvider(Provider):
    def __init__(self, response): self.response=response
    async def extract(self, prompt): return self.response

NULLABLE_STRING = {"type": "STRING", "nullable": True}
NULLABLE_NUMBER = {"type": "NUMBER", "nullable": True}
NULLABLE_INTEGER = {"type": "INTEGER", "nullable": True}
PRODUCT_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "name": NULLABLE_STRING, "brand": NULLABLE_STRING,
        "price": NULLABLE_NUMBER, "currency": NULLABLE_STRING,
        "availability": NULLABLE_STRING, "images": {"type": "ARRAY", "items": {"type": "STRING"}},
        "rating": NULLABLE_NUMBER, "review_count": NULLABLE_INTEGER,
        "description": NULLABLE_STRING, "specs": {"type": "OBJECT"},
    },
    "required": ["name", "brand", "price", "currency", "availability", "images", "rating", "review_count", "description", "specs"],
}
class GeminiProvider(Provider):
    """Gemini handles interpretation only; it is not given browsing tools."""
    def __init__(self, api_key=None, model=None):
        self.api_key=api_key or os.getenv("GEMINI_API_KEY", "")
        self.model=model or os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    async def status(self) -> dict:
        return {"configured": bool(self.api_key) and not self.api_key.startswith("replace_"), "model": self.model}
    async def extract(self, prompt: str) -> dict:
        if not (await self.status())["configured"]:
            raise LLMError("Gemini is not configured. Set GEMINI_API_KEY in .env (never commit or share it).")
        def request():
            client=genai.Client(api_key=self.api_key)
            interaction=client.interactions.create(model=self.model, input=prompt, response_format=[{"type":"text", "mime_type":"application/json", "schema":PRODUCT_SCHEMA}])
            return interaction.output_text
        try:
            text=await asyncio.to_thread(request)
            if not text: raise LLMError("Gemini completed without text JSON.")
            return json.loads(text)
        except LLMError: raise
        except Exception as exc:
            raise LLMError(f"Gemini extraction failed: {exc}") from exc
