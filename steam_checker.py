#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Console front-end for Steam checks."""
from __future__ import annotations

import io
import os
import sys

import steam_core as sc


if sys.platform == "win32":
    try:
        os.system("chcp 65001 >nul 2>&1")
    except Exception:
        pass
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True
    )


def safe_input(prompt: str = "") -> str:
    sys.stdout.write(prompt)
    sys.stdout.flush()
    try:
        return sys.stdin.buffer.readline().decode("utf-8", errors="replace").rstrip("\r\n")
    except Exception:
        return input()


def c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def clear_screen() -> None:
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass


def pause() -> None:
    safe_input(c("\n  Enter...", "33"))


def log_cli(msg: str, kind: str = "info") -> None:
    palette = {
        "info": "36",
        "ok": "32",
        "err": "31",
        "warn": "33",
        "dim": "90",
        "title": "1;36",
    }
    print(c(msg, palette.get(kind, "36")), flush=True)


def banner() -> None:
    art = [
        " ███████╗████████╗███████╗ █████╗ ███╗   ███╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ ",
        " ██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗",
        " ███████╗   ██║   █████╗  ███████║██╔████╔██║    ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝",
        " ╚════██║   ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗",
        " ███████║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║",
        " ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝",
    ]
    print(c("=" * 102, "36"))
    for line in art:
        print(c(line, "1;96"))
    print(c("=" * 102, "36"))
    print()


def apply_custom_aliases(cfg: dict) -> None:
    custom_aliases = cfg.get("custom_aliases", {})
    if not isinstance(custom_aliases, dict):
        return
    for alias, title in custom_aliases.items():
        if not isinstance(alias, str) or not isinstance(title, str):
            continue
        alias_key = alias.strip().lower()
        title_value = title.strip()
        if alias_key and title_value:
            sc.GAME_ALIASES[alias_key] = title_value


def show_status(cfg: dict) -> None:
    key = cfg.get("api_key", "")
    key_status = c("установлен", "32") if key else c("не задан", "31")
    custom_count = len(cfg.get("custom_aliases", {})) if isinstance(cfg.get("custom_aliases", {}), dict) else 0
    print(f"  API key : {key_status}")
    print(f"  Output  : {c(os.path.abspath(sc.OUTPUT_DIR), '36')}")
    print(f"  Accounts: {c(os.path.abspath(sc.ACCOUNTS_FILE), '36')}")
    print(f"  Aliases : {c(str(len(sc.GAME_ALIASES)), '36')} total, {c(str(custom_count), '33')} custom")
    print()


def menu() -> None:
    print(c("  [1] Запустить проверку", "36"))
    print(c("  [2] Изменить API key", "36"))
    print(c("  [3] Открыть папку результатов", "36"))
    print(c("  [4] Показать игры и алиасы", "36"))
    print(c("  [5] Добавить свой алиас", "36"))
    print(c("  [6] Выход", "36"))
    print()


def get_api_key(cfg: dict) -> str:
    if cfg.get("api_key"):
        return cfg["api_key"]

    print(c("  API key не задан.", "33"))
    key = safe_input(c("  Введите API key: ", "36")).strip()
    if key:
        cfg["api_key"] = key
        sc.save_config(cfg)
        print(c("  Ключ сохранен.", "32"))
    return key


def show_aliases() -> None:
    print(c("\n  Игры и алиасы", "1"))
    grouped: dict[str, list[str]] = {}
    for alias, title in sc.GAME_ALIASES.items():
        grouped.setdefault(title, []).append(alias)

    for title in sorted(grouped.keys(), key=str.casefold):
        aliases = ", ".join(sorted(grouped[title], key=str.casefold))
        print(c(f"\n  {title}", "36"))
        print(f"    {aliases}")


def add_custom_alias(cfg: dict) -> None:
    print(c("\n  Добавить свой алиас", "1"))
    alias = safe_input(c("  Алиас: ", "36")).strip().lower()
    if not alias:
        print(c("  Алиас не задан.", "31"))
        return

    title = safe_input(c("  Точное название игры: ", "36")).strip()
    if not title:
        print(c("  Название игры не задано.", "31"))
        return

    custom_aliases = cfg.get("custom_aliases", {})
    if not isinstance(custom_aliases, dict):
        custom_aliases = {}

    custom_aliases[alias] = title
    cfg["custom_aliases"] = custom_aliases
    sc.GAME_ALIASES[alias] = title
    sc.save_config(cfg)
    print(c(f"  Сохранено: {alias} -> {title}", "32"))


def input_games() -> list[str]:
    print(c("\n  Игры", "1"))
    print("  Вводите по одной игре или через запятую.")
    print("  Пустая строка завершает ввод.")
    games: list[str] = []
    while True:
        raw = safe_input(c(f"  Game [{len(games) + 1}]: ", "36")).strip()
        if raw == "":
            if games:
                break
            print(c("  Добавьте хотя бы одну игру.", "31"))
            continue
        for part in [p.strip() for p in raw.split(",") if p.strip()]:
            resolved = sc.resolve_game_name(part, log_cli)
            if resolved not in games:
                games.append(resolved)
                print(c(f"  + {resolved}", "32"))
    return games


def input_accounts() -> list[str]:
    print(c("\n  Аккаунты", "1"))
    print("  Один аккаунт на строку: nickname, SteamID64 или URL.")
    print(c("  Введите 'file', чтобы загрузить accounts.txt.", "33"))
    print("  Пустая строка завершает ввод.")
    accounts: list[str] = []
    while True:
        raw = safe_input(c(f"  Account [{len(accounts) + 1}]: ", "36")).strip()
        if raw == "":
            if accounts:
                break
            print(c("  Добавьте хотя бы один аккаунт.", "31"))
            continue
        if raw.lower() == "file":
            loaded = sc.load_accounts_from_file(sc.ACCOUNTS_FILE)
            if loaded:
                accounts.extend(loaded)
                print(c(f"  Загружено: {len(loaded)}", "32"))
            else:
                print(c("  accounts.txt не найден или пуст.", "31"))
            continue
        for part in [p.strip() for p in raw.split(",") if p.strip()]:
            accounts.append(part)
            print(c(f"  + {part}", "32"))
    return accounts


def print_summary(summary: list, games: list[str]) -> None:
    print(c("\n" + "=" * 72, "36"))
    print(c("  ИТОГОВЫЙ ОТЧЕТ", "1"))
    print(c("=" * 72, "36"))

    for game in sc.sort_game_names(games):
        found_count = 0
        missing_count = 0
        error_count = 0
        for _, _, item_game, status, _ in summary:
            if item_game != game:
                continue
            status_text = str(status).strip().upper()
            if status_text == "FOUND":
                found_count += 1
            elif status_text == "MISSING":
                missing_count += 1
            else:
                error_count += 1

        print(c(f"\n  {game}", "1"))
        print(c("  " + "-" * 68, "90"))
        print(f"  Есть    : {c(str(found_count), '32')}")
        print(f"  Нет     : {c(str(missing_count), '31')}")
        if error_count:
            print(f"  Ошибки  : {c(str(error_count), '33')}")

    print(c("\n  Результаты:", "36"), os.path.abspath(sc.OUTPUT_DIR))


def change_api_key(cfg: dict) -> None:
    print(c("\n  Изменить API key", "1"))
    key = safe_input(c("  Новый ключ: ", "36")).strip()
    if key:
        cfg["api_key"] = key
        sc.save_config(cfg)
        print(c("  Сохранено.", "32"))
    else:
        print(c("  Без изменений.", "33"))


def open_results_dir() -> None:
    sc.ensure_dir(sc.OUTPUT_DIR)
    if sys.platform == "win32":
        os.startfile(os.path.abspath(sc.OUTPUT_DIR))
        return
    os.system(f'xdg-open "{os.path.abspath(sc.OUTPUT_DIR)}" >/dev/null 2>&1')


def main_menu() -> None:
    clear_screen()
    banner()
    cfg = sc.load_config()
    apply_custom_aliases(cfg)

    while True:
        show_status(cfg)
        menu()
        choice = safe_input(c("  Выбор [1-6]: ", "36")).strip()

        if choice == "1":
            api_key = get_api_key(cfg)
            if not api_key:
                pause()
                clear_screen()
                banner()
                continue

            games = input_games()
            accounts = input_accounts()
            if not games or not accounts:
                print(c("  Нужны и игры, и аккаунты.", "31"))
                pause()
                clear_screen()
                banner()
                continue

            summary = sc.run_check(api_key, accounts, games, log_cli)
            print_summary(summary, games)
            pause()

        elif choice == "2":
            change_api_key(cfg)
            pause()

        elif choice == "3":
            open_results_dir()
            pause()

        elif choice == "4":
            show_aliases()
            pause()

        elif choice == "5":
            add_custom_alias(cfg)
            pause()

        elif choice == "6":
            print(c("\n  Пока!\n", "36"))
            return

        else:
            print(c("  Введите число от 1 до 6.\n", "31"))
            pause()

        clear_screen()
        banner()
        cfg = sc.load_config()
        apply_custom_aliases(cfg)


if __name__ == "__main__":
    sc.ensure_dir(sc.OUTPUT_DIR)
    sc.create_accounts_template()
    main_menu()
