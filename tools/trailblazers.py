import json
from datetime import datetime

import requests
from loguru import logger

from datatypes.account import AccountItem, TrailblazersItem
from datatypes.response import RankResponse, DomainResponse
from sdk.sql import SQL
from tools.session import get_proxied_session
from user_data.chains import taiko_chain


def get_trailblazers_rank(
        session: requests.Session(),
        account: AccountItem = None,
        address: str = None
) -> RankResponse:
    if account:
        address = account.address

    response = session.get(url=f"https://trailblazer.mainnet.taiko.xyz/s2/user/rank?address={address}")
    return RankResponse.parse_obj(json.loads(response.content))


def get_trailblazers_address(
        session: requests.Session(),
        account: AccountItem = None,
        address: str = None
) -> str:
    if account:
        address = account.address
    response = session.get(url=f"https://trailblazer.mainnet.taiko.xyz/s2/user/rank?address={address}")

    parsed = RankResponse.parse_obj(json.loads(response.content))
    if parsed.score:
        return address
    else:
        return address.lower()


def get_trailblazers_domain(session: requests.Session(), address: str) -> DomainResponse:
    response = session.get(url=f"https://trailblazer.mainnet.taiko.xyz/s2/user/domain?address={address}")
    return DomainResponse.parse_obj(json.loads(response.content))


def update_trailblazers_profile(sql: SQL, account: AccountItem):
    try:
        session = get_proxied_session(proxy=account.proxy)
        address = get_trailblazers_address(session=session, account=account)
        rank = get_trailblazers_rank(session=session, address=address)
        domain = get_trailblazers_domain(session=session, address=address)
        status = sql.add_trailblazers_report(trailblazers=TrailblazersItem(
            id=account.id,
            domain=domain.dotTaiko if domain.dotTaiko else '',
            points=rank.score,
            rank=rank.rank,
            last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        if status:
            logger.info(f'#{account.id} | {account.address}: #{rank.rank} with {rank.score} points | {status}.')
        else:
            logger.info(f'#{account.id} | {account.address}: #{rank.rank} with {rank.score} points.')
    except:
        logger.warning(f'#{account.id} | {account.address}: trailblazers_report error.')


def get_total_trailblazer_count(address: str):
    try:
        session = get_proxied_session()
        rank = get_trailblazers_rank(session=session, address=address)
        return rank.total
    except:
        return 999_999_999


def get_trailblazers_badge(
        session: requests.Session(), address: str,
        signature: str, timestamp: int, badge_id: int
):
    payload = {
        "address": address,
        "signature": signature,
        "message": str(timestamp),
        "badgeId": badge_id,
        "chainId": taiko_chain.id
    }

    response = session.post(url=f"https://trailblazer.mainnet.taiko.xyz/faction/mint", json=payload)
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        try:
            if 'Not Whitelisted' in str(json.loads(response.content)):
                return json.loads(response.content)
            else:
                logger.warning(response.content)
                return ''
        except:
            logger.warning(response.content)
            return ''


def get_week_badge_message(
        address: str,
        signature: str,
        timestamp: int,
        badge_id: int,
        proxy: str
):
    session = get_proxied_session(proxy=proxy)
    message = get_trailblazers_badge(
        session=session, address=address, signature=signature, timestamp=timestamp, badge_id=badge_id
    )
    return message
