from typing import Optional

from pydantic import BaseModel


class RankResponse(BaseModel):
    rank: int
    score: int
    total: int


class DomainResponse(BaseModel):
    dotTaiko: Optional[str]


class GalxeResponse(BaseModel):
    value: int
