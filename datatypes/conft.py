from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class CurrentChain(BaseModel):
    id: int
    network_id: int
    name: str
    slug: str
    rpcs: List[HttpUrl]
    custom_rpc: Optional[HttpUrl]
    explorers: List[HttpUrl]
    image_url: HttpUrl
    description: Optional[str]
    funding: Optional[str]
    backed: Optional[str]
    conft_slug: str
    conft_name: str
    reservoir_trading: bool
    source: str
    currency: dict
    reservoir_api_domain: Optional[str]
    bridge_urls: List[str]
    fetchConftNativeListings: bool
    isDomainsAvailable: bool


class Nft(BaseModel):
    blockchainName: str
    contractAddress: str
    tokenId: str
    name: str
    thumb: Optional[HttpUrl]
    rank: int
    collectionName: Optional[str]
    collectionSlug: Optional[str]
    collectionCover: Optional[str]
    floorPrice: Optional[float]
    averagePrice: Optional[float]
    bestBid: Optional[float]
    listingPrices: List[float]


class Meta(BaseModel):
    count: int


class WalletNfts(BaseModel):
    nfts: List[Nft]
    meta: Meta


class CollectionItemsResponse(BaseModel):
    walletNfts: Optional[WalletNfts]
    currentPage: int
    isOwnerWallet: bool
    pathname: str
    address: str
    blockchain: str
    selectedBlockchainFromCookie: str
    currentChain: CurrentChain


class Nonce(BaseModel):
    nonce: str


class NonceResponse(BaseModel):
    nonce: Nonce
    address: str
