from pydantic import BaseModel


class CollectorItem(BaseModel):
    id: int
    private_key: str
    cex_public: str
