"""A transparent, in-process guard for demo usage (not a billing system)."""
from __future__ import annotations
import os
from datetime import date
class DemoBudget:
    def __init__(self): self.day=date.today(); self.used=0
    def consume(self):
        if date.today() != self.day: self.day, self.used = date.today(), 0
        maximum=int(os.getenv("UPC_REMOTE_DAILY_LIMIT", "5"))
        if self.used >= maximum: raise RuntimeError(f"Demo remote-fetch limit of {maximum} per day reached.")
        self.used += 1
budget=DemoBudget()
