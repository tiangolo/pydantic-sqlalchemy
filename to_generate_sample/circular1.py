from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from .circular2 import Circular2


class Circular1(BaseModel):
    # import os
    circular2: Optional[Circular2] = None
    #
    # def test(self):
    #     print(self.os)