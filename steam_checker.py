#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI-обёртка над steam_core (логика проверки в steam_core)."""

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
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace"
    )


def safe_input(prompt=""):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    try:
        return sys.stdin.buffer.readline().decode("utf-8", errors="replace").rstrip(
            "\r\n"
        )
    except Exception:
        return input()


def c(text, code):
    return f"\033[{code}m{text}\033[0m"


def log_cli(msg: str, kind: str = "info") -> None:
    codes = {
        "info": "36",
        "ok": "32",
        "err": "31",
        "warn": "33",
        "dim": "90",
        "title": "1;36",
    }
    code = codes.get(kind, "36")
    print(c(msg, code))


def clear_screen():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass


def print_header():
    print(c("=" * 58, "36"))
    print(c("        STEAM GAME CHECKER  v2.0", "1"))
    print(c("  Проверка наличия игр через Steam Web API", "36"))
    print(c("=" * 58, "36"))
    print()


def sep(char="-", w=58, clr="35"):
    print(c(char * w, clr))


def get_api_key(cfg: dict) -> str:
    if cfg.get("api_key"):
        return cfg["api_key"]

    print(c("\n  [!] Steam Web API ключ не задан!", "33"))
    print()
    print("  Как получить БЕСПЛАТНЫЙ ключ (занимает 30 секунд):")
    print(c("  1. Открой: https://steamcommunity.com/dev/apikey", "36"))
    print("  2. Войди в Steam аккаунт")
    print("  3. Введи любое название сайта (например: localhost)")
    print("  4. Скопируй ключ и вставь сюда")
    print()

    key = safe_input(c("  Введи API ключ: ", "36")).strip()
    if key:
        cfg["api_key"] = key
        sc.save_config(cfg)
        print(c("  [+] Ключ сохранён в config.json", "32"))
    return key


def input_games():
    print(c("\n--- ИГРЫ ДЛЯ ПРОВЕРКИ ---", "1"))
    print("Введите игры для поиска (по одной или через запятую).")
    print(
        c(
            "Имя должно совпадать с названием в Steam (после псевдонима) — без частичного совпадения.",
            "33",
        )
    )
    print("Псевдонимы: 'кс го', 'дота', 'гта5', 'tf2', 'раст' и т.д.")
    print(c("Пустая строка или 'готово' -- завершить ввод.", "33"))
    print()

    games = []
    while True:
        raw = safe_input(c(f"  Игра [{len(games)+1}]: ", "36")).strip()
        if raw.lower() in ("готово", "done", "exit", ""):
            if games:
                break
            print(c("  Нужна хотя бы одна игра!", "31"))
            continue
        for part in [p.strip() for p in raw.split(",") if p.strip()]:
            resolved = sc.resolve_game_name(part, log_cli)
            games.append(resolved)
            print(c(f"  [+] {resolved}", "32"))
    return games


def input_accounts():
    print(c("\n--- АККАУНТЫ STEAM ---", "1"))
    print("Поддерживается:")
    print(c("  nickname", "36"))
    print(c("  https://steamcommunity.com/id/nickname/", "36"))
    print(c("  https://steamcommunity.com/profiles/76561198000000000/", "36"))
    print(c("  76561198000000000  (SteamID64)", "36"))
    print()
    print(c(f"  Введи 'файл' -- загрузить из {sc.ACCOUNTS_FILE}", "33"))
    print(c("  Пустая строка или 'готово' -- завершить.", "33"))
    print()

    accounts = []
    while True:
        raw = safe_input(c(f"  Аккаунт [{len(accounts)+1}]: ", "36")).strip()
        if raw.lower() in ("готово", "done", "exit", ""):
            if accounts:
                break
            print(c("  Нужен хотя бы один аккаунт!", "31"))
            continue
        if raw.lower() == "файл":
            loaded = sc.load_accounts_from_file(sc.ACCOUNTS_FILE)
            if not loaded:
                print(c(f"  Файл не найден или пуст.", "31"))
            else:
                accounts.extend(loaded)
                print(c(f"  [+] Загружено {len(loaded)} аккаунтов.", "32"))
            continue
        for part in [p.strip() for p in raw.split(",") if p.strip()]:
            accounts.append(part)
            print(c(f"  [+] {part}", "32"))
    return accounts


def print_summary(summary: list, games: list):
    print(c("\n" + "=" * 58, "36"))
    print(c("  ИТОГОВЫЙ ОТЧЁТ", "1"))
    print(c("=" * 58, "36"))

    for game in sc.sort_game_names(games):
        rows = [(a, sid, s, pt) for a, sid, g, s, pt in summary if g == game]

        found_rows = [(a, sid, pt) for a, sid, s, pt in rows if s == "ЕСТЬ"]
        nofound_rows = [(a, sid) for a, sid, s, pt in rows if s == "НЕТ"]
        error_rows = [(a, sid, s) for a, sid, s, pt in rows if s.startswith("ОШИБКА")]

        print(c(f"\n  Игра: {game}", "1"))
        sep()
        print(f"  Найдено    : {c(str(len(found_rows)), '32')} аккаунтов")
        print(f"  Не найдено : {c(str(len(nofound_rows)), '31')} аккаунтов")
        if error_rows:
            print(f"  Ошибки     : {c(str(len(error_rows)), '33')} аккаунтов")

        if found_rows:
            print(c("\n  >> ЕСТЬ игра:", "32"))
            for a, sid, pt in found_rows:
                print(c(f"     {a}", "32"))

        if nofound_rows:
            print(c("\n  -- НЕТ игры:", "31"))
            for a, sid in nofound_rows:
                print(c(f"     {a}", "31"))

        if error_rows:
            print(c("\n  ?? ОШИБКИ:", "33"))
            for a, sid, s in error_rows:
                print(c(f"     {a}  ->  {s}", "33"))

    abs_path = os.path.abspath(sc.OUTPUT_DIR)
    prof_path = os.path.abspath(sc.PROFILES_DIR)
    print(c(f"\n  Результаты по играм: {abs_path}", "36"))
    print(c(f"  Профили (только проверяемые игры в библиотеке): {prof_path}", "36"))
    print(c("  Структура:", "36"))
    for game in sc.sort_game_names(games):
        folder = sc.sanitize_name(game)
        print(c(f"    {folder}/", "33"))
        print(c("      found.txt      <- аккаунты, у которых есть эта игра", "32"))
        print(c(f"      not_found.txt  <- аккаунты без этой игры", "31"))
    print(c(f"    {os.path.basename(sc.PROFILES_DIR)}/", "33"))
    print(c("      <числовой_id>.txt  <- строка аккаунта и список найденных из проверки игр", "36"))

    print(c("\n" + "=" * 58, "36"))


def show_aliases():
    print(c("\n--- СЛОВАРЬ ПСЕВДОНИМОВ ---", "1"))
    sep()
    grouped = {}
    for alias, real in sc.GAME_ALIASES.items():
        grouped.setdefault(real, []).append(alias)
    for real in sorted(grouped.keys()):
        aliases_str = ", ".join(sorted(grouped[real]))
        print(f"  {c(real, '32')}  <-  {c(aliases_str, '33')}")
    sep()
    print()


def add_alias_interactive():
    print(c("\n--- ДОБАВИТЬ ПСЕВДОНИМ ---", "1"))
    alias = safe_input("  Псевдоним (например 'eft'): ").strip().lower()
    real = safe_input(
        "  Настоящее название (например 'Escape from Tarkov'): "
    ).strip()
    if alias and real:
        sc.GAME_ALIASES[alias] = real
        print(
            c(
                f"  [+] Добавлено: '{alias}' -> '{real}'  (только в этой сессии)",
                "32",
            )
        )
    else:
        print(c("  Ничего не добавлено.", "31"))


def change_api_key(cfg: dict):
    print(c("\n--- ИЗМЕНИТЬ API КЛЮЧ ---", "1"))
    print(c("  Получить ключ: https://steamcommunity.com/dev/apikey", "36"))
    key = safe_input("  Новый ключ: ").strip()
    if key:
        cfg["api_key"] = key
        sc.save_config(cfg)
        print(c("  [+] Ключ сохранён.", "32"))
    else:
        print(c("  Ключ не изменён.", "31"))


def main_menu():
    clear_screen()
    print_header()

    cfg = sc.load_config()

    while True:
        key_status = (
            c(cfg.get("api_key", "НЕ ЗАДАН")[:8] + "...", "32")
            if cfg.get("api_key")
            else c("НЕ ЗАДАН", "31")
        )
        print(c("  ГЛАВНОЕ МЕНЮ", "1"))
        print(f"  API ключ: {key_status}")
        print()
        print("  1. Начать проверку аккаунтов")
        print("  2. Показать словарь псевдонимов")
        print("  3. Добавить псевдоним")
        print("  4. Изменить API ключ")
        print("  5. Выход")
        print()

        choice = safe_input(c("  Выбор [1-5]: ", "36")).strip()

        if choice == "1":
            api_key = get_api_key(cfg)
            if not api_key:
                print(c("  Без API ключа проверка невозможна!", "31"))
                safe_input(c("  Enter...", "33"))
                clear_screen()
                print_header()
                continue

            games = input_games()
            accounts = input_accounts()

            if not games or not accounts:
                print(c("  Нужны и игры, и аккаунты!", "31"))
                safe_input(c("\n  Enter...", "33"))
                clear_screen()
                print_header()
                continue

            summary = sc.run_check(api_key, accounts, games, log_cli)
            print_summary(summary, games)

            safe_input(c("\n  Нажми Enter для возврата в меню...", "33"))
            clear_screen()
            print_header()

        elif choice == "2":
            show_aliases()
            safe_input(c("  Enter...", "33"))
            clear_screen()
            print_header()

        elif choice == "3":
            add_alias_interactive()
            safe_input(c("\n  Enter...", "33"))
            clear_screen()
            print_header()

        elif choice == "4":
            change_api_key(cfg)
            safe_input(c("\n  Enter...", "33"))
            clear_screen()
            print_header()

        elif choice == "5":
            print(c("\n  Пока!\n", "36"))
            sys.exit(0)

        else:
            print(c("  Введи цифру от 1 до 5.\n", "31"))


if __name__ == "__main__":
    sc.ensure_dir(sc.OUTPUT_DIR)
    sc.create_accounts_template()
    main_menu()
