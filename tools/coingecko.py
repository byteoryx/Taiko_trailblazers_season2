from loguru import logger

from sdk.pycoingecko import CoinGeckoAPI


def get_asset_price(
        ticker: str,
        proxy: str = 'socks5://aqvja29v66:o7kd9j4gio@premium2.travchisproxies.com:51204'
) -> float:
    cg = CoinGeckoAPI(proxy=proxy)
    if 'usd' in ticker:
        return 1
    else:
        try:
            price = cg.get_price(ids=ticker, vs_currencies='usd')
            return price[ticker]['usd']
        except Exception as e:
            if 'eth' in ticker:
                return 3000
            logger.exception(e)
            return 0
