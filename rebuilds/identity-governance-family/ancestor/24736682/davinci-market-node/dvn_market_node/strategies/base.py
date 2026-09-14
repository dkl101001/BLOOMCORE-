from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

from ..types import Hypothesis, MarketFrame, OrderIntent


class Strategy(ABC):
    @abstractmethod
    def run(self, *, eq_id: str, frame: MarketFrame, params: Dict[str, Any]) -> Tuple[List[Hypothesis], List[OrderIntent], Dict[str, Any]]:
        raise NotImplementedError
