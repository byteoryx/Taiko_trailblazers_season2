from typing import Optional

from pydantic import BaseModel


class LockupItem(BaseModel):
    timestamp: Optional[int]
    amount: Optional[int]
    lockup: Optional[int]
