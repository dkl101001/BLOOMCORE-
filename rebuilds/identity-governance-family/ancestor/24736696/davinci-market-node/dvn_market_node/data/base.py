from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict

from ..types import MarketFrame


class DataAdapter(ABC):
    @abstractmethod
    def snapshot(self, eq_id: str, timestamp_ny: str) -> MarketFrame:
        raise NotImplementedError
