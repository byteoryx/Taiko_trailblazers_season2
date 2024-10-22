shuffle_accounts = True  # перемешивать ли аккаунты перед стартом работы
workers_range = (1, 1)  # максимальное количество кошельков для одновременной работы
sleep_between_txs_in_sec = (10, 30)  # сон между любыми действиями
sleep_after_loop_in_sec = (60 * 60 * 1, 60 * 60 * 2)  # сон между циклами
leaderboard_update_on_script_start = True  # начинать ли работу скрипта с парсинга актуального лидерборда
leaderboard_update_on_every_module_start = False  # обновлять ли позицию аккаунта в лидерборде при запуске любого модуля
db_filename = 'data'

deposit_from_source_chains_to_taiko = True  # депозитить ли баланс из source_chains в taiko
withdraw_from_taiko_to_source_chains = False  # выводить ли баланс из taiko в source_chains и в дальнейшем на cex
bridges_to_use = ['xy', 'orbiter']  # 'xy', 'orbiter'

minimum_transfer = 0.001  # какой объём использовать для бриджей, чтобы не сжигать eth на нулёвые транзакции
minimum_taiko_balance = 0.0001  # если баланс аккаунта меньше указанного, то он не будет использоваться для работы
gas_multiplier = 2  # множитель газа

# для того чтобы выключить модуль, укажите диапазон (0, 0)
wraps_range = (0, 0)  # количество врапов внутри одного цикла для одного аккаунта, затраты $0.01
conft_mint_range = (0, 0)  # количество минтов conft внутри одного цикла для одного аккаунта, затраты $1.3
omnihub_mint_range = (0, 0)  # количество минтов omnihub внутри одного цикла для одного аккаунта, затраты $0.35
rubyscore_votes_range = (0, 0)  # количество votes внутри одного цикла для одного аккаунта, затраты $0.01
rhino_gms_range = (0, 0)  # количество gms внутри одного цикла для одного аккаунта, затраты $0.15
self_transfer_range = (0, 0)  # количество селф-трансферов эфира, затраты $0.01
burner_transfer_range = (0, 0)  # количество трансферов на пустой кошелёк и обратно, затраты $0.01
brigade_game = False  # несколько уникальных около-бесплатных взаимодействий с brigadegame.io, затраты $0.01
crack_x_stack_range = (0, 0)  # клейм бесплатных игр в crackandstack.com, затраты $0.01
zypher2048_range = (0, 0)  # старт игры в zypher.game/2048, затраты $0.7
oxastra_boost = False  # ежедневный чекин в 0xastra.xyz, затраты $0.01
contract_deploy_range = (0, 0)  # создание пустого контракта, затраты $0.1

# taikodrips
taikodrips_stake = False  # включить или отключить модуль стейка на taikodrips.xyz
taikodrips_lock_in_days_range = [60, 91]  # доступные варианты: 60, 91, 182, 365
