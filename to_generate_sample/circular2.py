from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .circular1 import Circular1


@dataclass
class Circular2:
    circular1: Circular1


