from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from urllib.parse import urlparse

class Product(BaseModel):
    """The public contract: exactly ten normalized product fields."""
    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    brand: str | None = None
    price: float | None = None
    currency: str | None = None
    availability: str | None = None
    images: list[str] = Field(default_factory=list)
    rating: float | None = None
    review_count: int | None = None
    description: str | None = None
    specs: dict[str, str] = Field(default_factory=dict)

    @field_validator("name", "brand", "availability", "description", mode="before")
    @classmethod
    def strings(cls, value: Any):
        if value is None: return None
        value = str(value).strip()
        return value or None

    @field_validator("currency", mode="before")
    @classmethod
    def currency_code(cls, value: Any):
        if value is None: return None
        value = str(value).strip().upper()
        return value if len(value) == 3 and value.isalpha() else None

    @field_validator("price", "rating", mode="before")
    @classmethod
    def nonnegative_number(cls, value: Any):
        if value is None or value == "": return None
        value = float(value)
        if value < 0: raise ValueError("must not be negative")
        return value

    @field_validator("review_count", mode="before")
    @classmethod
    def count(cls, value: Any):
        if value is None or value == "": return None
        value = int(value)
        if value < 0: raise ValueError("must not be negative")
        return value

    @field_validator("images", mode="before")
    @classmethod
    def valid_images(cls, value: Any):
        seen, result = set(), []
        for item in value or []:
            url = str(item).strip()
            if url and urlparse(url).scheme in {"http", "https"} and url not in seen:
                seen.add(url); result.append(url)
        return result

    @field_validator("specs", mode="before")
    @classmethod
    def clean_specs(cls, value: Any):
        return {str(k).strip(): str(v).strip() for k, v in (value or {}).items() if str(k).strip() and str(v).strip()}

class FieldEvidence(BaseModel):
    source: str
    excerpt: str
    status: str = "supported"

class ExtractionReport(BaseModel):
    confidence: dict[str, str] = Field(default_factory=dict)
    evidence: dict[str, list[FieldEvidence]] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    diagnostics: dict[str, Any] = Field(default_factory=dict)
