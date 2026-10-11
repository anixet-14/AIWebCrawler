import asyncio
import pytest
from app.models.product import Product
from app.crawler.safety import validate_url, URLSafetyError
from app.crawler.cloudflare import validate_remote_url, RemoteFetchError
from app.extraction.content import collect_evidence
from app.services.validation import metadata_product
def test_schema_is_exact_and_normalizes():
    p=Product(price="19.95",currency="usd",images=["https://x/a.jpg","https://x/a.jpg","ftp://no"],specs={" Weight ":" 2 kg ","":"x"})
    assert list(p.model_dump())==["name","brand","price","currency","availability","images","rating","review_count","description","specs"]
    assert p.currency=="USD" and p.images==["https://x/a.jpg"] and p.specs=={"Weight":"2 kg"}
def test_rejects_private_url(monkeypatch):
    monkeypatch.setattr("socket.getaddrinfo",lambda *a,**k:[(2,1,6,"",("127.0.0.1",0))])
    with pytest.raises(URLSafetyError): validate_url("http://example.test/item")
def test_jsonld_metadata_fallback():
    html='''<html><head><script type="application/ld+json">{"@type":"Product","name":"Orbit Lamp","brand":{"name":"Acme"},"image":"/lamp.jpg","offers":{"price":"29.99","priceCurrency":"USD"},"aggregateRating":{"ratingValue":"4.6","reviewCount":"18"}}</script></head><body><h1>Orbit Lamp</h1></body></html>'''
    product, report=metadata_product(collect_evidence(html,"https://example.com/p"))
    assert product.name=="Orbit Lamp" and product.price==29.99 and product.images==["https://example.com/lamp.jpg"]
def test_bad_count():
    with pytest.raises(ValueError): Product(review_count=-1)
def test_remote_mode_rejects_local_without_dns_lookup():
    with pytest.raises(RemoteFetchError): validate_remote_url("http://localhost/private")
    assert validate_remote_url("https://shop.example/product?x=1") == "https://shop.example/product?x=1"
