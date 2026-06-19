# Steam Account Checker

Консольная программа для проверки Steam-аккаунтов по списку игр.

## Что умеет

- проверять аккаунты по нику, SteamID64 или ссылке на профиль
- искать игры по точному названию и по алиасам
- показывать список игр и алиасов
- добавлять свои алиасы
- сохранять результаты в `steam_results`

## Запуск

```bash
pip install -r requirements.txt
python steam_checker.py
```

## Как пользоваться

1. Запусти `steam_checker.py`
2. Введи Steam Web API key
3. Укажи игры для проверки
4. Укажи аккаунты
5. Запусти проверку

Аккаунты можно вводить:

- по одному на строку
- через запятую
- через `accounts.txt`

Поддерживаются:

- `nickname`
- `https://steamcommunity.com/id/...`
- `https://steamcommunity.com/profiles/...`
- `SteamID64`

## Результаты

После проверки появляются файлы:

- `steam_results/<игра>/found.txt`
- `steam_results/<игра>/not_found.txt`
- `steam_results/profiles/<SteamID64>.txt`

## Файлы

- `steam_checker.py` — меню и запуск
- `steam_core.py` — основная логика
- `requirements.txt` — зависимости

## Примечание

Не выкладывай свой `config.json`, если там лежит API key.
