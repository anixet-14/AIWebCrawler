from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from app.models.product import Product
from app.extraction.providers import GeminiProvider
from app.crawler.cloudflare import configured
from app.services.pipeline import extract_product
app=FastAPI(title="Universal AI Product Crawler", version="0.1.0")
class ExtractRequest(BaseModel): url: str; use_llm: bool=True; debug: bool=False; fetch_mode: str="cloudflare"
@app.get("/health")
async def health(): return {"status":"ok","gemini":await GeminiProvider().status()}
@app.get("/api/config")
async def config(): return {"llm_provider":"Gemini API (hosted inference)","gemini":await GeminiProvider().status(), "remote_fetch_provider":"Cloudflare Browser Run", "cloudflare_configured":configured(), "default_fetch_mode":"cloudflare", "paid_apis":False}
@app.post("/api/validate")
async def validate(product: Product): return product.model_dump()
@app.post("/api/extract")
async def extract(request: ExtractRequest):
    try:
        product,report=await extract_product(request.url,request.use_llm,request.fetch_mode)
        result={"product":product.model_dump()}
        if request.debug: result["report"]=report.model_dump()
        return result
    except (ValueError, RuntimeError) as exc: raise HTTPException(status_code=400,detail=str(exc))
    except Exception as exc: raise HTTPException(status_code=502,detail=f"Extraction failed: {exc}")
