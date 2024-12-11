from typing import List, Optional

from pydantic import BaseModel, Field


class IDModel(BaseModel):
    chain: str
    address: str


class ItemModel(BaseModel):
    deployer: str
    interactionsCounter: int
    lastInteractionAt: str
    deployedAt: int
    id: IDModel = Field(..., alias='_id')


class PaginationModel(BaseModel):
    limit: int
    skip: int
    totalItems: int


class RhinoContractsResponse(BaseModel):
    items: List[Optional[ItemModel]]
    pagination: PaginationModel
