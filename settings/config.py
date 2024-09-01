shuffle_accounts = True  # перемешивать ли аккаунты перед стартом работы
workers_range = (1, 1)  # максимальное количество кошельков для одновременной работы
sleep_between_txs_in_sec = (5, 10)  # сон между любыми действиями
sleep_after_loop_in_sec = (60 * 60 * 1, 60 * 60 * 2)  # сон между циклами

deposit_from_source_chains_to_taiko = True  # депозитить ли баланс из source_chains в taiko
withdraw_from_taiko_to_source_chains = True  # выводить ли баланс из taiko в source_chains
bridges_to_use = ['xy', 'orbiter']  # 'xy', 'orbiter'

leave_on_source = 0.0051  # какой баланс в eth оставлять на source_chain или taiko после бриджа
minimum_transfer = 0.1  # какой объём использовать для бриджей, чтобы не сжигать eth на нулёвые транзакции
minimum_withdraw_from_taiko_transfer = 0.001  # какой объём использовать для вывода из taiko
minimum_taiko_balance = 0.0001  # если баланс меньше указанного, то аккаунт не будет использоваться для ончейн активности

# для того чтобы выключить модуль, просто укажите диапазон (0, 0)
wraps_range = (1, 5)  # количество врапов внутри одного цикла для одного аккаунта, затраты $0.01
conft_mint_range = (0, 1)  # количество минтов conft внутри одного цикла для одного аккаунта, затраты $1.3
omnihub_mint_range = (0, 1)  # количество минтов omnihub внутри одного цикла для одного аккаунта, затраты $0.35
rubyscore_votes_range = (1, 5)  # количество votes внутри одного цикла для одного аккаунта, затраты $0.01
rhino_gms_range = (0, 1)  # количество gms внутри одного цикла для одного аккаунта, затраты $0.15
self_transfer_range = (1, 5)  # количество селф-трансферов эфира, затраты $0.01
burner_transfer_range = (1, 5)  # количество трансферов на пустой кошелёк и обратно, затраты $0.01
brigade_nft_claim = True  # клейм нфт раз в 8 часов из игры brigadegame.io, затраты $0.01
crack_x_stack_range = (1, 5)  # клейм бесплатных игр в crackandstack.com, затраты $0.01
zypher2048_range = (0, 1)  # старт игры в zypher.game/2048, затраты $0.7
