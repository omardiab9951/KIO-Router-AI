"""Interfaces shared by all routers."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class RouterOutput:
    label: str
    flag: Optional[int]
    confidence: Optional[float]
    raw: str
    latency_ms: float
    status: str
    router_name: str


class BaseRouter:
    name = "base"

    def predict(self, message: str) -> RouterOutput:
        raise NotImplementedError

