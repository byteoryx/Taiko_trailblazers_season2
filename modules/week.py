import time
from datetime import datetime

from loguru import logger
from web3 import Web3

from datatypes.account import DayBridgeItem, BadgeItem
from sdk.sql import SQL
from settings.chains import taiko_chain
from tools.crypto import get_balance, get_badge_signature, week8_tx
from tools.trailblazers import get_week_badge_message


def week_main(
        index: int,
        private_key: str,
        sql: SQL,
        day: str,
        badge_id: int = 7
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    timestamp = int(time.time() * 1000)
    signature = get_badge_signature(private_key=private_key, timestamp=timestamp)
    message = get_week_badge_message(address=account.address,
                                     signature=signature,
                                     timestamp=timestamp,
                                     badge_id=badge_id)

    if message:
        if 'Not Whitelisted' not in str(message):
            old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
            if old_balance.float > 0.00001:
                tx_hash = week8_tx(
                    private_key=private_key,
                    message=message
                )
                if tx_hash and 'already minted' in tx_hash:
                    status = sql.add_badge_report(
                        badge_id=badge_id + 1,
                        badge_item=BadgeItem(
                            id=index,
                            minted="True",
                            last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ),
                        acc_id=index
                    )
                    logger.success(f'#{index} | {account.address}: week already minted | {status}.')
                    return 'already minted'
                elif tx_hash:
                    new_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
                    new_costs = old_balance.float - new_balance.float

                    volume, txs, costs = sql.get_volume_and_txs_by_id(day=day, acc_id=index)
                    status = sql.add_bridge_day_report(
                        day_item=DayBridgeItem(
                            id=index,
                            txs=txs,
                            volume=volume,
                            costs=costs + new_costs,
                            last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ),
                        day=day,
                        acc_id=index
                    )

                    logger.info(f'#{index} | {account.address}: week | {taiko_chain.explorer}/{tx_hash} | {status}.')
                    return 'minted'
                else:
                    logger.error(f'#{index} | {account.address}: week tx has failed.')
                    return 'failed'
            else:
                logger.warning(f'#{index} | {account.address}: week | {old_balance.float} $ETH on {taiko_chain.name}, '
                               f'minimum required: 0.001 $ETH.')
                return 'failed'
        else:
            logger.warning(f'#{index} | {account.address}: week | not whitelisted yet.')
            return 'not whitelisted'
    else:
        logger.error(f'#{index} | {account.address}: week couldnt get a message.')
        return 'failed'
