from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..types import ExecutionResult, OrderIntent


class Broker(ABC):
    @abstractmethod
    def submit(self, intent: OrderIntent) -> ExecutionResult:
        raise NotImplementedError

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        raise NotImplementedError
