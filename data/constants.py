from datatypes.crypto import Token
from user_data.config import db_filename

version = 'v2.0'

database_path = f'./data/{db_filename}.db'
private_keys_path = './user_data/private.txt'
rhino_contracts_path = './user_data/rhino.txt'

orbiter_contract = "0xe4edb277e41dc89ab076a1f049f4a3efa700bce8"
owlto_contract = "0x5e809A85Aa182A9921EDD10a4163745bb3e36284"
conft_contract = "0x9059ca87ddc891b91e731c57d21809f1a4adc8d9"
conft_mint_price = 0.00039
omnihub_contract = "0x8cdf3095E4Cf64F08C3734bF564516689ec0BDc2"
omnihub_mint_price_int = 1049515774996480
rubyscore_contract = "0x4D1E2145082d0AB0fDa4a973dC4887C7295e21aB"
rhino_gm_price = 0.0000335
hana_supply_contract = "0xB9eD09af341a59c05c8AaE584172e8dCc1E828b6"
hana_token_repay_borrow_contract = "0x4aB85Bf9EA548410023b25a13031E91B4c4f3b91"
hana_eth_repay_borrow_contract = "0xB9eD09af341a59c05c8AaE584172e8dCc1E828b6"

meridian_deposit_contract = "0x1697A950a67d9040464287b88fCa6cb5FbEC09BA"
kiloex_deposit_contract = "0x2646E743A8F47b8d2427dBcc10f89e911f2dBBaa"

eth_contract = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
hana_weth_supplied_contract = "0xacd2E13C933aE1EF97698f00D14117BB70C77Ef1"
hana_weth_debt_contract = "0xf1777ead4098f574c68e59905588f3c9875251ed"
hana_usdc_stg_debt_contract = "0xe5e8fe8e8891123ff9994734c3dcdca7500b3d79"
hana_usdc_debt_contract = "0x0247606c3D3F62213bbC9D7373318369e6860eb1"
hana_taiko_debt_contract = "0x1592Ff6f057d65a17Be56116e2B3cbfD4d2314C2"

taiko_weth_contract = "0xA51894664A773981C6C112C43ce576f315d5b1B6"
taiko_usdc_stg_contract = "0x19e26B0638bf63aa9fa4d14c6baF8D52eBE86C5C"
taiko_usdc_contract = "0x07d83526730c7438048d55a4fc0b850e2aab6f0b"
taiko_taiko_contract = "0xa9d23408b9ba935c230493c40c73824df71a0975"

xy_contracts = {
    'opt': "0x7a6e01880693093abACcF442fcbED9E0435f1030",
    'eth': "0x4315f344a905dC21a08189A117eFd6E1fcA37D57",
    'arb': "0x33383265290421C704c6b09F4BF27ce574DC4203",
    'scroll': "0x778C974568e376146dbC64fF12aD55B2d1c4133f",
    'linea': "0x73Ce60416035B8D7019f6399778c14ccf5C9c7A1",
    'base': "0x73Ce60416035B8D7019f6399778c14ccf5C9c7A1",
    'taiko': "0x73Ce60416035B8D7019f6399778c14ccf5C9c7A1"
}
xy_aggregator_contract = "0x18b1751a6f4ec773faf8e1a24ed0c3b271e538c"

brigade_harvest_contract = "0x8a93AAE6D94680658012B887BfDd981A17661Ef4"
brigade_spin_contract = "0x03376f22eF7d08CEE420D07207f85E52638A9fCd"
brigade_capsule_contract = "0x0158A4055428b67e286b2627e91120b49ca1146c"
brigade_starship_contract = "0x73716C57f87fFd4135453aBCe6cf61Bb0E99C410"
brigade_checkin_contract = "0x20F50518188FB3c9F5adff472E056291C4B98ecE"
brigade_claim_item_contract = "0x72dCB9a28bB8EA172B58130d9fd17A6dBE7A9E41"
crack_x_stack_contract = "0x009C32F03d6eEa4F6DA9DD3f8EC7Dc85824Ae0e6"
zypher2048_contract = "0xd4629d312CdC663D062F3Fbc322534A9Df0151bC"
week_badge_contract = "0xa20a8856e00F5ad024a55A663F06DCc419FFc4d5"
meridian_deposited_usdc = "0xa3f248A1779364FB8B6b59304395229ea8241229"

ritsu_swap_contract = "0x7160570BB153Edd0Ea1775EC2b2Ac9b65F1aB61B"
ritsu_pools = {
    'USDC': "0xeF4a016F3E54c4520220adE7a496842ECbF83E09",
    'TKO': "0x3BEbD0720F857DeF80af8dd44B5970A3749743Bc",
    'USDCe': "0x7c38E9389B27668280E5aaAc372eBCb2ECc1c5E0",
    'ETH-USDCe': "0xE75bfdbBE463A4c562F69B45f3A302faC4BB9E16"
}
taikodrips_contract = "0xf90209C44dBf5Fa3d40ac85a008206b5A8c24899"
taikodrips_minimum_amount = 0.01

badge_collection_contract = "0xa20a8856e00f5ad024a55a663f06dcc419ffc4d5"

eth_token = Token(
    address='0x0000000000000000000000000000000000000000',
    ticker='ETH',
    coingecko_ticker='ethereum',
    denomination=10 ** 18
)

weth_token = Token(
    address='0xA51894664A773981C6C112C43ce576f315d5b1B6',
    ticker='WETH',
    coingecko_ticker='ethereum',
    denomination=10 ** 18
)

usdc_token = Token(
    address='0x07d83526730c7438048d55a4fc0b850e2aab6f0b',
    ticker='USDC',
    coingecko_ticker='usd-coin',
    denomination=10 ** 6
)

usdce_token = Token(
    address='0x19e26B0638bf63aa9fa4d14c6baF8D52eBE86C5C',
    ticker='USDCe',
    coingecko_ticker='usd-coin',
    denomination=10 ** 6
)

taiko_token = Token(
    address=taiko_taiko_contract,
    ticker='TKO',
    coingecko_ticker='taiko',
    denomination=10 ** 18
)
