from pydantic import BaseModel


class ChainItem(BaseModel):
    name: str
    id: int
    orbiter_code: int
    rpc: str
    explorer: str


source_chains = [
    ChainItem(
        name='arb',
        id=42161,
        orbiter_code=9002,
        rpc='https://arbitrum.llamarpc.com',
        explorer='https://arbiscan.io/tx'
    ),
    ChainItem(
        name='opt',
        id=10,
        orbiter_code=9007,
        rpc='https://rpc.ankr.com/optimism',
        explorer='https://optimistic.etherscan.io/tx'
    ),
    ChainItem(
        name='base',
        id=8453,
        orbiter_code=9021,
        rpc='https://rpc.ankr.com/base',
        explorer='https://basescan.org/tx'
    ),
    ChainItem(
        name='linea',
        id=59144,
        orbiter_code=9023,
        rpc='https://linea.blockpi.network/v1/rpc/public',
        explorer='https://lineascan.build/tx'
    )
]

destination_chains = [
    ChainItem(
        name='arb',
        id=42161,
        orbiter_code=9002,
        rpc='https://arbitrum.llamarpc.com',
        explorer='https://arbiscan.io/tx'
    ),
    ChainItem(
        name='opt',
        id=10,
        orbiter_code=9007,
        rpc='https://rpc.ankr.com/optimism',
        explorer='https://optimistic.etherscan.io/tx'
    ),
    ChainItem(
        name='base',
        id=8453,
        orbiter_code=9021,
        rpc='https://rpc.ankr.com/base',
        explorer='https://basescan.org/tx'
    )
]

taiko_chain = ChainItem(
    name='taiko',
    id=167000,
    orbiter_code=9020,
    rpc='https://rpc.ankr.com/taiko',
    explorer='https://taikoscan.io/tx'
)
