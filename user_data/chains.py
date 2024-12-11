from pydantic import BaseModel


class ChainItem(BaseModel):
    name: str
    id: int
    orbiter_code: int
    gas_zip_code: int
    rpc: str
    explorer: str

    def __hash__(self):
        return hash((self.name, self.id, self.orbiter_code, self.gas_zip_code, self.rpc, self.explorer))


source_chains = [
    ChainItem(
        name='opt',
        id=10,
        orbiter_code=9007,
        gas_zip_code=55,
        rpc='https://rpc.ankr.com/optimism',
        explorer='https://optimistic.etherscan.io/tx'
    ),
    ChainItem(
        name='arb',
        id=42161,
        orbiter_code=9002,
        gas_zip_code=57,
        rpc='https://rpc.ankr.com/arbitrum',
        explorer='https://arbiscan.io/tx'
    ),
    ChainItem(
        name='base',
        id=8453,
        orbiter_code=9021,
        gas_zip_code=54,
        rpc='https://rpc.ankr.com/base',
        explorer='https://basescan.org/tx'
    ),
    ChainItem(
        name='scroll',
        id=534352,
        orbiter_code=9019,
        gas_zip_code=41,
        rpc='https://rpc.ankr.com/scroll',
        explorer='https://scrollscan.com/tx',
    )
]

destination_chains = [
    ChainItem(
        name='opt',
        id=10,
        orbiter_code=9007,
        gas_zip_code=55,
        rpc='https://rpc.ankr.com/optimism',
        explorer='https://optimistic.etherscan.io/tx'
    ),
    ChainItem(
        name='arb',
        id=42161,
        orbiter_code=9002,
        gas_zip_code=57,
        rpc='https://rpc.ankr.com/arbitrum',
        explorer='https://arbiscan.io/tx'
    ),
    ChainItem(
        name='base',
        id=8453,
        orbiter_code=9021,
        gas_zip_code=54,
        rpc='https://rpc.ankr.com/base',
        explorer='https://basescan.org/tx'
    ),
    ChainItem(
        name='scroll',
        id=534352,
        orbiter_code=9019,
        gas_zip_code=41,
        rpc='https://rpc.ankr.com/scroll',
        explorer='https://scrollscan.com/tx',
    )
]

taiko_chain = ChainItem(
    name='taiko',
    id=167000,
    orbiter_code=9020,
    gas_zip_code=249,
    rpc='https://rpc.ankr.com/taiko',
    explorer='https://taikoscan.io/tx'
)
