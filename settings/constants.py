version = 'v2.0'

database_path = './data/data.db'
private_keys_path = './data/private.txt'
rhino_contracts_path = './data/rhino.txt'

gas_multiplier = 2.5

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

brigade_nft_contract = "0x8a93AAE6D94680658012B887BfDd981A17661Ef4"
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
ritsu_swap_abi = [
    {"inputs": [{"internalType": "address", "name": "_wETH", "type": "address"}], "stateMutability": "nonpayable",
     "type": "constructor"}, {"inputs": [], "name": "ApproveFailed", "type": "error"},
    {"inputs": [], "name": "ETHTransferFailed", "type": "error"}, {"inputs": [], "name": "Expired", "type": "error"},
    {"inputs": [], "name": "NotEnoughLiquidityMinted", "type": "error"},
    {"inputs": [], "name": "TooLittleReceived", "type": "error"},
    {"inputs": [], "name": "TransferFailed", "type": "error"},
    {"inputs": [], "name": "TransferFromFailed", "type": "error"}, {"anonymous": False, "inputs": [
        {"indexed": True, "internalType": "address", "name": "previousOwner", "type": "address"},
        {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}],
                                                                    "name": "OwnershipTransferred", "type": "event"}, {
        "inputs": [{"internalType": "address", "name": "pool", "type": "address"}, {
            "components": [{"internalType": "address", "name": "token", "type": "address"},
                           {"internalType": "uint256", "name": "amount", "type": "uint256"}],
            "internalType": "struct RitsuRouter.TokenInput[]", "name": "inputs", "type": "tuple[]"},
                   {"internalType": "bytes", "name": "data", "type": "bytes"},
                   {"internalType": "uint256", "name": "minLiquidity", "type": "uint256"},
                   {"internalType": "address", "name": "callback", "type": "address"},
                   {"internalType": "bytes", "name": "callbackData", "type": "bytes"},
                   {"internalType": "address", "name": "staking", "type": "address"}], "name": "addLiquidity",
        "outputs": [{"internalType": "uint256", "name": "liquidity", "type": "uint256"}], "stateMutability": "payable",
        "type": "function"}, {"inputs": [{"internalType": "address", "name": "pool", "type": "address"}, {
        "components": [{"internalType": "address", "name": "token", "type": "address"},
                       {"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "internalType": "struct RitsuRouter.TokenInput[]", "name": "inputs", "type": "tuple[]"},
                                         {"internalType": "bytes", "name": "data", "type": "bytes"},
                                         {"internalType": "uint256", "name": "minLiquidity", "type": "uint256"},
                                         {"internalType": "address", "name": "callback", "type": "address"},
                                         {"internalType": "bytes", "name": "callbackData", "type": "bytes"},
                                         {"internalType": "address", "name": "staking", "type": "address"}],
                              "name": "addLiquidity2",
                              "outputs": [{"internalType": "uint256", "name": "liquidity", "type": "uint256"}],
                              "stateMutability": "payable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "pool", "type": "address"}, {
            "components": [{"internalType": "address", "name": "token", "type": "address"},
                           {"internalType": "uint256", "name": "amount", "type": "uint256"}],
            "internalType": "struct RitsuRouter.TokenInput[]", "name": "inputs", "type": "tuple[]"},
                   {"internalType": "bytes", "name": "data", "type": "bytes"},
                   {"internalType": "uint256", "name": "minLiquidity", "type": "uint256"},
                   {"internalType": "address", "name": "callback", "type": "address"},
                   {"internalType": "bytes", "name": "callbackData", "type": "bytes"}, {
                       "components": [{"internalType": "address", "name": "token", "type": "address"},
                                      {"internalType": "uint256", "name": "approveAmount", "type": "uint256"},
                                      {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                                      {"internalType": "uint8", "name": "v", "type": "uint8"},
                                      {"internalType": "bytes32", "name": "r", "type": "bytes32"},
                                      {"internalType": "bytes32", "name": "s", "type": "bytes32"}],
                       "internalType": "struct IRouter.SplitPermitParams[]", "name": "permits", "type": "tuple[]"},
                   {"internalType": "address", "name": "staking", "type": "address"}], "name": "addLiquidityWithPermit",
        "outputs": [{"internalType": "uint256", "name": "liquidity", "type": "uint256"}], "stateMutability": "payable",
        "type": "function"}, {"inputs": [{"internalType": "address", "name": "pool", "type": "address"}, {
        "components": [{"internalType": "address", "name": "token", "type": "address"},
                       {"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "internalType": "struct RitsuRouter.TokenInput[]", "name": "inputs", "type": "tuple[]"},
                                         {"internalType": "bytes", "name": "data", "type": "bytes"},
                                         {"internalType": "uint256", "name": "minLiquidity", "type": "uint256"},
                                         {"internalType": "address", "name": "callback", "type": "address"},
                                         {"internalType": "bytes", "name": "callbackData", "type": "bytes"}, {
                                             "components": [
                                                 {"internalType": "address", "name": "token", "type": "address"},
                                                 {"internalType": "uint256", "name": "approveAmount",
                                                  "type": "uint256"},
                                                 {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                                                 {"internalType": "uint8", "name": "v", "type": "uint8"},
                                                 {"internalType": "bytes32", "name": "r", "type": "bytes32"},
                                                 {"internalType": "bytes32", "name": "s", "type": "bytes32"}],
                                             "internalType": "struct IRouter.SplitPermitParams[]", "name": "permits",
                                             "type": "tuple[]"},
                                         {"internalType": "address", "name": "staking", "type": "address"}],
                              "name": "addLiquidityWithPermit2",
                              "outputs": [{"internalType": "uint256", "name": "liquidity", "type": "uint256"}],
                              "stateMutability": "payable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "pool", "type": "address"},
                   {"internalType": "uint256", "name": "liquidity", "type": "uint256"},
                   {"internalType": "bytes", "name": "data", "type": "bytes"},
                   {"internalType": "uint256[]", "name": "minAmounts", "type": "uint256[]"},
                   {"internalType": "address", "name": "callback", "type": "address"},
                   {"internalType": "bytes", "name": "callbackData", "type": "bytes"}], "name": "burnLiquidity",
        "outputs": [{"components": [{"internalType": "address", "name": "token", "type": "address"},
                                    {"internalType": "uint256", "name": "amount", "type": "uint256"}],
                     "internalType": "struct IPool.TokenAmount[]", "name": "amounts", "type": "tuple[]"}],
        "stateMutability": "nonpayable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "pool", "type": "address"},
                   {"internalType": "uint256", "name": "liquidity", "type": "uint256"},
                   {"internalType": "bytes", "name": "data", "type": "bytes"},
                   {"internalType": "uint256", "name": "minAmount", "type": "uint256"},
                   {"internalType": "address", "name": "callback", "type": "address"},
                   {"internalType": "bytes", "name": "callbackData", "type": "bytes"}], "name": "burnLiquiditySingle",
        "outputs": [{"components": [{"internalType": "address", "name": "token", "type": "address"},
                                    {"internalType": "uint256", "name": "amount", "type": "uint256"}],
                     "internalType": "struct IPool.TokenAmount", "name": "amountOut", "type": "tuple"}],
        "stateMutability": "nonpayable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "pool", "type": "address"},
                   {"internalType": "uint256", "name": "liquidity", "type": "uint256"},
                   {"internalType": "bytes", "name": "data", "type": "bytes"},
                   {"internalType": "uint256", "name": "minAmount", "type": "uint256"},
                   {"internalType": "address", "name": "callback", "type": "address"},
                   {"internalType": "bytes", "name": "callbackData", "type": "bytes"}, {
                       "components": [{"internalType": "uint256", "name": "approveAmount", "type": "uint256"},
                                      {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                                      {"internalType": "bytes", "name": "signature", "type": "bytes"}],
                       "internalType": "struct IRouter.ArrayPermitParams", "name": "permit", "type": "tuple"}],
        "name": "burnLiquiditySingleWithPermit", "outputs": [{"components": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}],
            "internalType": "struct IPool.TokenAmount",
            "name": "amountOut", "type": "tuple"}],
        "stateMutability": "nonpayable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "pool", "type": "address"},
                   {"internalType": "uint256", "name": "liquidity", "type": "uint256"},
                   {"internalType": "bytes", "name": "data", "type": "bytes"},
                   {"internalType": "uint256[]", "name": "minAmounts", "type": "uint256[]"},
                   {"internalType": "address", "name": "callback", "type": "address"},
                   {"internalType": "bytes", "name": "callbackData", "type": "bytes"}, {
                       "components": [{"internalType": "uint256", "name": "approveAmount", "type": "uint256"},
                                      {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                                      {"internalType": "bytes", "name": "signature", "type": "bytes"}],
                       "internalType": "struct IRouter.ArrayPermitParams", "name": "permit", "type": "tuple"}],
        "name": "burnLiquidityWithPermit", "outputs": [{"components": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}],
            "internalType": "struct IPool.TokenAmount[]", "name": "amounts",
            "type": "tuple[]"}], "stateMutability": "nonpayable",
        "type": "function"}, {"inputs": [{"internalType": "address", "name": "_factory", "type": "address"},
                                         {"internalType": "bytes", "name": "data", "type": "bytes"}],
                              "name": "createPool",
                              "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                              "stateMutability": "payable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "", "type": "address"},
                   {"internalType": "uint256", "name": "", "type": "uint256"}], "name": "enteredPools",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view",
        "type": "function"},
    {"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "enteredPoolsLength",
     "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view",
     "type": "function"}, {"inputs": [{"internalType": "address", "name": "", "type": "address"},
                                      {"internalType": "address", "name": "", "type": "address"}],
                           "name": "isPoolEntered", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                           "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "bytes[]", "name": "data", "type": "bytes[]"}], "name": "multicall",
     "outputs": [{"internalType": "bytes[]", "name": "results", "type": "bytes[]"}], "stateMutability": "payable",
     "type": "function"},
    {"inputs": [], "name": "owner", "outputs": [{"internalType": "address", "name": "", "type": "address"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "renounceOwnership", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "token", "type": "address"},
                   {"internalType": "address", "name": "to", "type": "address"},
                   {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "rescueERC20",
        "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {
        "inputs": [{"internalType": "address payable", "name": "to", "type": "address"},
                   {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "rescueETH",
        "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "token", "type": "address"},
                   {"internalType": "uint256", "name": "value", "type": "uint256"},
                   {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                   {"internalType": "uint8", "name": "v", "type": "uint8"},
                   {"internalType": "bytes32", "name": "r", "type": "bytes32"},
                   {"internalType": "bytes32", "name": "s", "type": "bytes32"}], "name": "selfPermit", "outputs": [],
        "stateMutability": "payable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "token", "type": "address"},
                   {"internalType": "uint256", "name": "value", "type": "uint256"},
                   {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                   {"internalType": "bytes", "name": "signature", "type": "bytes"}], "name": "selfPermit2",
        "outputs": [], "stateMutability": "payable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "token", "type": "address"},
                   {"internalType": "uint256", "name": "value", "type": "uint256"},
                   {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                   {"internalType": "bytes", "name": "signature", "type": "bytes"}], "name": "selfPermit2IfNecessary",
        "outputs": [], "stateMutability": "payable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "token", "type": "address"},
                   {"internalType": "uint256", "name": "nonce", "type": "uint256"},
                   {"internalType": "uint256", "name": "expiry", "type": "uint256"},
                   {"internalType": "uint8", "name": "v", "type": "uint8"},
                   {"internalType": "bytes32", "name": "r", "type": "bytes32"},
                   {"internalType": "bytes32", "name": "s", "type": "bytes32"}], "name": "selfPermitAllowed",
        "outputs": [], "stateMutability": "payable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "token", "type": "address"},
                   {"internalType": "uint256", "name": "nonce", "type": "uint256"},
                   {"internalType": "uint256", "name": "expiry", "type": "uint256"},
                   {"internalType": "uint8", "name": "v", "type": "uint8"},
                   {"internalType": "bytes32", "name": "r", "type": "bytes32"},
                   {"internalType": "bytes32", "name": "s", "type": "bytes32"}], "name": "selfPermitAllowedIfNecessary",
        "outputs": [], "stateMutability": "payable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "token", "type": "address"},
                   {"internalType": "uint256", "name": "value", "type": "uint256"},
                   {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                   {"internalType": "uint8", "name": "v", "type": "uint8"},
                   {"internalType": "bytes32", "name": "r", "type": "bytes32"},
                   {"internalType": "bytes32", "name": "s", "type": "bytes32"}], "name": "selfPermitIfNecessary",
        "outputs": [], "stateMutability": "payable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "target", "type": "address"},
                   {"internalType": "address", "name": "token", "type": "address"},
                   {"internalType": "uint256", "name": "amount", "type": "uint256"},
                   {"internalType": "address", "name": "to", "type": "address"}], "name": "stake", "outputs": [],
        "stateMutability": "nonpayable", "type": "function"}, {
        "inputs": [{"internalType": "address", "name": "target", "type": "address"},
                   {"internalType": "address", "name": "token", "type": "address"},
                   {"internalType": "uint256", "name": "amount", "type": "uint256"},
                   {"internalType": "address", "name": "to", "type": "address"}], "name": "stakeWithToken",
        "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"components": [{
        "components": [
            {
                "internalType": "address",
                "name": "pool",
                "type": "address"},
            {
                "internalType": "bytes",
                "name": "data",
                "type": "bytes"},
            {
                "internalType": "address",
                "name": "callback",
                "type": "address"},
            {
                "internalType": "bytes",
                "name": "callbackData",
                "type": "bytes"}],
        "internalType": "struct IRouter.SwapStep[]",
        "name": "steps",
        "type": "tuple[]"},
        {
            "internalType": "address",
            "name": "tokenIn",
            "type": "address"},
        {
            "internalType": "uint256",
            "name": "amountIn",
            "type": "uint256"}],
        "internalType": "struct IRouter.SwapPath[]",
        "name": "paths",
        "type": "tuple[]"},
        {"internalType": "uint256",
         "name": "amountOutMin",
         "type": "uint256"},
        {"internalType": "uint256",
         "name": "deadline",
         "type": "uint256"}],
        "name": "swap", "outputs": [{
            "components": [
                {
                    "internalType": "address",
                    "name": "token",
                    "type": "address"},
                {
                    "internalType": "uint256",
                    "name": "amount",
                    "type": "uint256"}],
            "internalType": "struct IPool.TokenAmount",
            "name": "amountOut",
            "type": "tuple"}],
        "stateMutability": "payable",
        "type": "function"}, {"inputs": [{
        "components": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "pool",
                        "type": "address"},
                    {
                        "internalType": "bytes",
                        "name": "data",
                        "type": "bytes"},
                    {
                        "internalType": "address",
                        "name": "callback",
                        "type": "address"},
                    {
                        "internalType": "bytes",
                        "name": "callbackData",
                        "type": "bytes"}],
                "internalType": "struct IRouter.SwapStep[]",
                "name": "steps",
                "type": "tuple[]"},
            {
                "internalType": "address",
                "name": "tokenIn",
                "type": "address"},
            {
                "internalType": "uint256",
                "name": "amountIn",
                "type": "uint256"}],
        "internalType": "struct IRouter.SwapPath[]",
        "name": "paths",
        "type": "tuple[]"},
        {
            "internalType": "uint256",
            "name": "amountOutMin",
            "type": "uint256"},
        {
            "internalType": "uint256",
            "name": "deadline",
            "type": "uint256"},
        {
            "components": [
                {
                    "internalType": "address",
                    "name": "token",
                    "type": "address"},
                {
                    "internalType": "uint256",
                    "name": "approveAmount",
                    "type": "uint256"},
                {
                    "internalType": "uint256",
                    "name": "deadline",
                    "type": "uint256"},
                {
                    "internalType": "uint8",
                    "name": "v",
                    "type": "uint8"},
                {
                    "internalType": "bytes32",
                    "name": "r",
                    "type": "bytes32"},
                {
                    "internalType": "bytes32",
                    "name": "s",
                    "type": "bytes32"}],
            "internalType": "struct IRouter.SplitPermitParams",
            "name": "permit",
            "type": "tuple"}],
        "name": "swapWithPermit",
        "outputs": [{
            "components": [
                {
                    "internalType": "address",
                    "name": "token",
                    "type": "address"},
                {
                    "internalType": "uint256",
                    "name": "amount",
                    "type": "uint256"}],
            "internalType": "struct IPool.TokenAmount",
            "name": "amountOut",
            "type": "tuple"}],
        "stateMutability": "payable",
        "type": "function"},
    {"inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}], "name": "transferOwnership",
     "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "wETH", "outputs": [{"internalType": "address", "name": "", "type": "address"}],
     "stateMutability": "view", "type": "function"}]
