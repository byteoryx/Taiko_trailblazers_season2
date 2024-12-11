from typing import List, Optional

from pydantic import BaseModel


class CurrencyMetadata(BaseModel):
    logoURI: Optional[str]
    verified: bool
    isNative: bool


class Currency(BaseModel):
    chainId: int
    address: str
    symbol: str
    name: str
    decimals: int
    metadata: CurrencyMetadata


class FeeDetails(BaseModel):
    currency: Currency
    amount: str
    amountFormatted: str
    amountUsd: str


class SlippageTolerance(BaseModel):
    usd: Optional[str]
    value: Optional[str]
    percent: Optional[str]


class OperationDetails(BaseModel):
    operation: str
    sender: str
    recipient: str
    currencyIn: FeeDetails
    currencyOut: FeeDetails
    totalImpact: Optional[SlippageTolerance]
    swapImpact: Optional[SlippageTolerance]
    rate: str
    slippageTolerance: dict
    timeEstimate: int
    userBalance: str


class Check(BaseModel):
    endpoint: str
    method: str


class TransactionData(BaseModel):
    from_address: Optional[str]
    to: str
    data: str
    value: str
    maxFeePerGas: str
    maxPriorityFeePerGas: str
    chainId: int


class TransactionItem(BaseModel):
    status: str
    data: TransactionData
    check: Check


class Step(BaseModel):
    id: str
    action: str
    description: str
    kind: str
    requestId: str
    items: List[TransactionItem]


class Fees(BaseModel):
    gas: FeeDetails
    relayer: FeeDetails
    relayerGas: FeeDetails
    relayerService: FeeDetails
    app: FeeDetails


class RelayBridgeQuotes(BaseModel):
    steps: List[Step]
    fees: Optional[Fees]
    details: OperationDetails
