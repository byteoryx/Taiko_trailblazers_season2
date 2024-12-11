# перемешивать ли аккаунты перед стартом работы
shuffle_accounts = True
# максимальное количество кошельков для одновременной работы
workers_range = (1, 1)
# сон между любыми действиями
sleep_between_txs_in_sec = (10, 30)
# сон между циклами
sleep_after_loop_in_sec = (60 * 60 * 1, 60 * 60 * 2)
# начинать ли работу скрипта с парсинга актуального лидерборда
leaderboard_update_on_script_start = True
# обновлять ли позицию аккаунта в лидерборде при запуске любого модуля
leaderboard_update_on_every_module_start = False
# для удобства быстрого переключения между файлами баз данных
db_filename = 'data'
# множитель газа
gas_multiplier = 2
