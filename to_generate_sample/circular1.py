from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .circular2 import Circular2


@dataclass
class Circular1:
    circular2: Circular2
