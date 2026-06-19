#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
import sys
import time
from typing import Callable, Optional

import requests

def _default_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = _default_base_dir()

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
ACCOUNTS_FILE = os.path.join(BASE_DIR, "accounts.txt")
OUTPUT_DIR = os.path.join(BASE_DIR, "steam_results")
PROFILES_DIR = os.path.join(OUTPUT_DIR, "profiles")
REQUEST_DELAY = 1.2

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

LogFn = Optional[Callable[[str, str], None]]


def _log(log_fn: LogFn, msg: str, kind: str = "info") -> None:
    if log_fn:
        log_fn(msg, kind)


GAME_ALIASES = {
    "кс": "Counter-Strike 2",
    "кс го": "Counter-Strike 2",
    "кс2": "Counter-Strike 2",
    "кс 2": "Counter-Strike 2",
    "csgo": "Counter-Strike 2",
    "cs go": "Counter-Strike 2",
    "cs2": "Counter-Strike 2",
    "cs 2": "Counter-Strike 2",
    "counter strike": "Counter-Strike 2",
    "counter-strike": "Counter-Strike 2",
    "counter strike 2": "Counter-Strike 2",
    "контр страйк": "Counter-Strike 2",
    "контра": "Counter-Strike 2",
    "кс 1.6": "Counter-Strike",
    "cs 1.6": "Counter-Strike",
    "cs16": "Counter-Strike",
    "counter-strike 1.6": "Counter-Strike",
    "дота": "Dota 2",
    "dota": "Dota 2",
    "дота 2": "Dota 2",
    "dota 2": "Dota 2",
    "дота2": "Dota 2",
    "dota2": "Dota 2",
    "дотка": "Dota 2",
    "доту": "Dota 2",
    "доту 2": "Dota 2",
    "гта": "Grand Theft Auto V",
    "gta": "Grand Theft Auto V",
    "гта 5": "Grand Theft Auto V",
    "гта5": "Grand Theft Auto V",
    "gta5": "Grand Theft Auto V",
    "gta v": "Grand Theft Auto V",
    "гта v": "Grand Theft Auto V",
    "гта онлайн": "Grand Theft Auto V",
    "gta online": "Grand Theft Auto V",
    "гта ол": "Grand Theft Auto V",
    "гта5 онлайн": "Grand Theft Auto V",
    "джи ти а": "Grand Theft Auto V",
    "раст": "Rust",
    "rust": "Rust",
    "апекс": "Apex Legends",
    "apex": "Apex Legends",
    "апекс легендс": "Apex Legends",
    "apex legends": "Apex Legends",
    "пубг": "PUBG: BATTLEGROUNDS",
    "pubg": "PUBG: BATTLEGROUNDS",
    "пабг": "PUBG: BATTLEGROUNDS",
    "батлграундс": "PUBG: BATTLEGROUNDS",
    "пабджи": "PUBG: BATTLEGROUNDS",
    "киберпанк": "Cyberpunk 2077",
    "cyberpunk": "Cyberpunk 2077",
    "кибер": "Cyberpunk 2077",
    "cp2077": "Cyberpunk 2077",
    "ведьмак": "The Witcher 3: Wild Hunt",
    "witcher": "The Witcher 3: Wild Hunt",
    "ведьмак 3": "The Witcher 3: Wild Hunt",
    "witcher 3": "The Witcher 3: Wild Hunt",
    "вичер": "The Witcher 3: Wild Hunt",
    "в3": "The Witcher 3: Wild Hunt",
    "террария": "Terraria",
    "terraria": "Terraria",
    "амонг ас": "Among Us",
    "among us": "Among Us",
    "амонг": "Among Us",
    "амонгас": "Among Us",
    "элден ринг": "ELDEN RING",
    "elden ring": "ELDEN RING",
    "элден": "ELDEN RING",
    "секиро": "Sekiro: Shadows Die Twice",
    "sekiro": "Sekiro: Shadows Die Twice",
    "секиро тени": "Sekiro: Shadows Die Twice",
    "дарк соулс 3": "DARK SOULS III",
    "dark souls 3": "DARK SOULS III",
    "ds3": "DARK SOULS III",
    "дс3": "DARK SOULS III",
    "дарк соулс": "DARK SOULS III",
    "dark souls": "DARK SOULS III",
    "дарк соулс ремастер": "DARK SOULS™: REMASTERED",
    "dark souls remastered": "DARK SOULS™: REMASTERED",
    "ds1": "DARK SOULS™: REMASTERED",
    "вальхейм": "Valheim",
    "valheim": "Valheim",
    "тф2": "Team Fortress 2",
    "tf2": "Team Fortress 2",
    "team fortress": "Team Fortress 2",
    "тим фортрес": "Team Fortress 2",
    "варфрейм": "Warframe",
    "warframe": "Warframe",
    "l4d2": "Left 4 Dead 2",
    "лфд2": "Left 4 Dead 2",
    "left 4 dead": "Left 4 Dead 2",
    "лфтд": "Left 4 Dead 2",
    "гмод": "Garry's Mod",
    "gmod": "Garry's Mod",
    "garrys mod": "Garry's Mod",
    "римворлд": "RimWorld",
    "rimworld": "RimWorld",
    "стардью": "Stardew Valley",
    "stardew": "Stardew Valley",
    "stardew valley": "Stardew Valley",
    "стардью вэлли": "Stardew Valley",
    "поэ": "Path of Exile",
    "poe": "Path of Exile",
    "path of exile": "Path of Exile",
    "патч оф экзайл": "Path of Exile",
    "арк": "ARK: Survival Evolved",
    "ark": "ARK: Survival Evolved",
    "арк выживание": "ARK: Survival Evolved",
    "хогвартс": "Hogwarts Legacy",
    "hogwarts": "Hogwarts Legacy",
    "хогвартс легаси": "Hogwarts Legacy",
    "дбд": "Dead by Daylight",
    "dbd": "Dead by Daylight",
    "dead by daylight": "Dead by Daylight",
    "фол гайс": "Fall Guys",
    "fall guys": "Fall Guys",
    "фолгайс": "Fall Guys",
    "море воров": "Sea of Thieves",
    "sea of thieves": "Sea of Thieves",
    "аид": "Hades",
    "hades": "Hades",
    "монстер хантер": "Monster Hunter: World",
    "mhw": "Monster Hunter: World",
    "monster hunter world": "Monster Hunter: World",
    "мхв": "Monster Hunter: World",
    "сатисфактори": "Satisfactory",
    "satisfactory": "Satisfactory",
    "бф": "Battlefield 2042",
    "bf": "Battlefield 2042",
    "bf2042": "Battlefield 2042",
    "battlefield 2042": "Battlefield 2042",
    "bf1": "Battlefield™ 1",
    "бф1": "Battlefield™ 1",
    "bfv": "Battlefield™ V",
    "бф5": "Battlefield™ V",
    "bf5": "Battlefield™ V",
    "дейс гон": "Days Gone",
    "days gone": "Days Gone",
    "холлоу найт": "Hollow Knight",
    "hollow knight": "Hollow Knight",
    "дрг": "Deep Rock Galactic",
    "drg": "Deep Rock Galactic",
    "дип рок": "Deep Rock Galactic",
    "рок и камень": "Deep Rock Galactic",
    "no mans sky": "No Man's Sky",
    "но мэнс скай": "No Man's Sky",
    "nms": "No Man's Sky",
    "субнаутика": "Subnautica",
    "subnautica": "Subnautica",
    "портал": "Portal 2",
    "portal": "Portal 2",
    "portal 2": "Portal 2",
    "халф лайф": "Half-Life 2",
    "hl2": "Half-Life 2",
    "half life": "Half-Life 2",
    "half-life 2": "Half-Life 2",
    "тарков": "Escape from Tarkov",
    "tarkov": "Escape from Tarkov",
    "eft": "Escape from Tarkov",
    "бг3": "Baldur's Gate 3",
    "bg3": "Baldur's Gate 3",
    "baldur": "Baldur's Gate 3",
    "балдурс гейт": "Baldur's Gate 3",
    "baldurs gate 3": "Baldur's Gate 3",
    "старфилд": "Starfield",
    "starfield": "Starfield",
    "рдр2": "Red Dead Redemption 2",
    "rdr2": "Red Dead Redemption 2",
    "red dead": "Red Dead Redemption 2",
    "ред дед": "Red Dead Redemption 2",
    "палворлд": "Palworld",
    "palworld": "Palworld",
    "пал мир": "Palworld",
    "дестини": "Destiny 2",
    "destiny": "Destiny 2",
    "destiny 2": "Destiny 2",
    "дестини 2": "Destiny 2",
    "лост арк": "Lost Ark",
    "lost ark": "Lost Ark",
    "рокет лиг": "Rocket League",
    "rocket league": "Rocket League",
    "рл": "Rocket League",
    "овервотч": "Overwatch® 2",
    "overwatch": "Overwatch® 2",
    "ow2": "Overwatch® 2",
    "ов2": "Overwatch® 2",
    "радуга": "Tom Clancy's Rainbow Six® Siege",
    "r6": "Tom Clancy's Rainbow Six® Siege",
    "r6s": "Tom Clancy's Rainbow Six® Siege",
    "сидж": "Tom Clancy's Rainbow Six® Siege",
    "rainbow six": "Tom Clancy's Rainbow Six® Siege",
    "скайрим": "The Elder Scrolls V: Skyrim",
    "skyrim": "The Elder Scrolls V: Skyrim",
    "tes v": "The Elder Scrolls V: Skyrim",
    "фоллаут 4": "Fallout 4",
    "fallout 4": "Fallout 4",
    "ф4": "Fallout 4",
    "fo4": "Fallout 4",
    "фоллаут 76": "Fallout 76",
    "fallout 76": "Fallout 76",
    "fo76": "Fallout 76",
    "цивилизация": "Sid Meier's Civilization VI",
    "civ 6": "Sid Meier's Civilization VI",
    "civ6": "Sid Meier's Civilization VI",
    "цив 6": "Sid Meier's Civilization VI",
    "eu4": "Europa Universalis IV",
    "ев4": "Europa Universalis IV",
    "европа": "Europa Universalis IV",
    "hoi4": "Hearts of Iron IV",
    "хойка": "Hearts of Iron IV",
    "хой4": "Hearts of Iron IV",
    "ck3": "Crusader Kings III",
    "кк3": "Crusader Kings III",
    "крусадер кингс": "Crusader Kings III",
    "stellaris": "Stellaris",
    "стелларис": "Stellaris",
    "тотал вар": "Total War: WARHAMMER III",
    "warhammer 3": "Total War: WARHAMMER III",
    "вархаммер 3": "Total War: WARHAMMER III",
    "ситис": "Cities: Skylines",
    "cities skylines": "Cities: Skylines",
    "симс 4": "The Sims™ 4",
    "sims 4": "The Sims™ 4",
    "the sims 4": "The Sims™ 4",
    "форза 5": "Forza Horizon 5",
    "forza 5": "Forza Horizon 5",
    "fh5": "Forza Horizon 5",
    "msfs": "Microsoft Flight Simulator",
    "флайт сим": "Microsoft Flight Simulator",
    "ets2": "Euro Truck Simulator 2",
    "евро трек": "Euro Truck Simulator 2",
    "евротрак": "Euro Truck Simulator 2",
    "пейдей": "PAYDAY 2",
    "payday 2": "PAYDAY 2",
    "payday2": "PAYDAY 2",
    "бордерлендс 3": "Borderlands 3",
    "borderlands 3": "Borderlands 3",
    "bl3": "Borderlands 3",
    "тайна тина": "Tiny Tina's Wonderlands",
    "tiny tina": "Tiny Tina's Wonderlands",
    "ре4": "Resident Evil 4",
    "re4": "Resident Evil 4",
    "resident evil 4": "Resident Evil 4",
    "ре2": "Resident Evil 2",
    "re2": "Resident Evil 2",
    "ре8": "Resident Evil Village",
    "re8": "Resident Evil Village",
    "resident evil village": "Resident Evil Village",
    "дмс": "Devil May Cry 5",
    "dmc5": "Devil May Cry 5",
    "devil may cry 5": "Devil May Cry 5",
    "год оф вар": "God of War",
    "god of war": "God of War",
    "спайдер": "Marvel's Spider-Man Remastered",
    "spider-man": "Marvel's Spider-Man Remastered",
    "человек паук": "Marvel's Spider-Man Remastered",
    "хорайзен": "Horizon Zero Dawn™ Complete Edition",
    "horizon zero dawn": "Horizon Zero Dawn™ Complete Edition",
    "hzd": "Horizon Zero Dawn™ Complete Edition",
    "тлоу": "The Last of Us™ Part I",
    "last of us": "The Last of Us™ Part I",
    "tlou": "The Last of Us™ Part I",
    "нью ворлд": "New World",
    "new world": "New World",
    "зомбоид": "Project Zomboid",
    "project zomboid": "Project Zomboid",
    "7 days": "7 Days to Die",
    "7дтд": "7 Days to Die",
    "семь дней": "7 Days to Die",
    "фазма": "Phasmophobia",
    "phasmophobia": "Phasmophobia",
    "фазмофобия": "Phasmophobia",
    "летал": "Lethal Company",
    "lethal company": "Lethal Company",
    "контент варнинг": "Content Warning",
    "content warning": "Content Warning",
    "вампайр": "Vampire Survivors",
    "vampire survivors": "Vampire Survivors",
    "факторио": "Factorio",
    "factorio": "Factorio",
    "кербал": "Kerbal Space Program",
    "ksp": "Kerbal Space Program",
    "kerbal": "Kerbal Space Program",
    "oxygen not included": "Oxygen Not Included",
    "кислород": "Oxygen Not Included",
    "донт старв": "Don't Starve Together",
    "dont starve": "Don't Starve Together",
    "dst": "Don't Starve Together",
    "капхед": "Cuphead",
    "cuphead": "Cuphead",
    "селеста": "Celeste",
    "celeste": "Celeste",
    "андертейл": "Undertale",
    "undertale": "Undertale",
    "slime rancher 2": "Slime Rancher 2",
    "slime rancher": "Slime Rancher 2",
    "слайм ранчер": "Slime Rancher 2",
    "powerwash": "PowerWash Simulator",
    "керхер": "PowerWash Simulator",
    "флиппер": "House Flipper",
    "house flipper": "House Flipper",
    "хитман": "HITMAN 3",
    "hitman 3": "HITMAN 3",
    "hitman": "HITMAN 3",
    "дисхоноред": "Dishonored 2",
    "dishonored": "Dishonored 2",
    "прей": "Prey",
    "prey": "Prey",
    "метро": "Metro Exodus",
    "metro exodus": "Metro Exodus",
    "метро исход": "Metro Exodus",
    "сталкер": "S.T.A.L.K.E.R. 2: Heart of Chornobyl",
    "stalker 2": "S.T.A.L.K.E.R. 2: Heart of Chornobyl",
    "сталкер 2": "S.T.A.L.K.E.R. 2: Heart of Chornobyl",
    "вар тандер": "War Thunder",
    "war thunder": "War Thunder",
    "смайт": "SMITE",
    "smite": "SMITE",
    "паладинс": "Paladins",
    "paladins": "Paladins",
    "бравлхалла": "Brawlhalla",
    "brawlhalla": "Brawlhalla",
    "осу": "osu!",
    "osu": "osu!",
    "osu!": "osu!",
    "geometry dash": "Geometry Dash",
    "гд": "Geometry Dash",
    "геометри даш": "Geometry Dash",
    "фм": "Football Manager 2024",
    "football manager": "Football Manager 2024",
    "fm24": "Football Manager 2024",
    "nba": "NBA 2K24",
    "nba 2k": "NBA 2K24",
    "мк11": "Mortal Kombat 11",
    "mk11": "Mortal Kombat 11",
    "теккен": "TEKKEN 8",
    "tekken 8": "TEKKEN 8",
    "tekken": "TEKKEN 8",
    "стрит файтер": "Street Fighter™ 6",
    "sf6": "Street Fighter™ 6",
    "street fighter 6": "Street Fighter™ 6",
    "фор хонор": "FOR HONOR™",
    "for honor": "FOR HONOR™",
    "дивижн 2": "Tom Clancy's The Division 2",
    "division 2": "Tom Clancy's The Division 2",
    "нойта": "Noita",
    "noita": "Noita",
    "рор2": "Risk of Rain 2",
    "risk of rain 2": "Risk of Rain 2",
    "ганфайр": "Gunfire Reborn",
    "gunfire reborn": "Gunfire Reborn",
    "сыновья леса": "Sons Of The Forest",
    "sons of the forest": "Sons Of The Forest",
    "sotf": "Sons Of The Forest",
    "the forest": "The Forest",
    "форест": "The Forest",
    "граундед": "Grounded",
    "grounded": "Grounded",
    "астронир": "ASTRONEER",
    "astroneer": "ASTRONEER",
    "рафт": "Raft",
    "raft": "Raft",
    "грин хелл": "Green Hell",
    "green hell": "Green Hell",
    "лонг дарк": "The Long Dark",
    "long dark": "The Long Dark",
    "ведьмак 2": "The Witcher 2: Assassins of Kings",
    "witcher 2": "The Witcher 2: Assassins of Kings",
    "масс эффект": "Mass Effect™ Legendary Edition",
    "mass effect": "Mass Effect™ Legendary Edition",
    "драгон эйдж": "Dragon Age™: Inquisition",
    "dragon age": "Dragon Age™: Inquisition",
    "лего звездные": "LEGO® Star Wars™: The Skywalker Saga",
    "lego star wars": "LEGO® Star Wars™: The Skywalker Saga",
    "джедай": "STAR WARS Jedi: Survivor",
    "jedi survivor": "STAR WARS Jedi: Survivor",
    "fallen order": "STAR WARS Jedi: Fallen Order",
    "джедай упавший": "STAR WARS Jedi: Fallen Order",
    "атомик": "Atomic Heart",
    "atomic heart": "Atomic Heart",
    "контрол": "Control Ultimate Edition",
    "control": "Control Ultimate Edition",
    "дет стрендинг": "DEATH STRANDING DIRECTOR'S CUT",
    "death stranding": "DEATH STRANDING DIRECTOR'S CUT",
    "мгс": "METAL GEAR SOLID V: THE PHANTOM PAIN",
    "mgsv": "METAL GEAR SOLID V: THE PHANTOM PAIN",
    "metal gear": "METAL GEAR SOLID V: THE PHANTOM PAIN",
    "nier": "NieR:Automata",
    "ниер": "NieR:Automata",
    "persona 5": "Persona 5 Royal",
    "персона 5": "Persona 5 Royal",
    "p5r": "Persona 5 Royal",
    "persona 4": "Persona 4 Golden",
    "п4г": "Persona 4 Golden",
    "mhr": "MONSTER HUNTER RISE",
    "mh rise": "MONSTER HUNTER RISE",
    "райз": "MONSTER HUNTER RISE",
    "ран": "Ready or Not",
    "ready or not": "Ready or Not",
    "инсурженси": "Insurgency: Sandstorm",
    "insurgency": "Insurgency: Sandstorm",
    "сквад": "Squad",
    "squad": "Squad",
    "hll": "Hell Let Loose",
    "hell let loose": "Hell Let Loose",
    "арма 3": "Arma 3",
    "arma 3": "Arma 3",
    "дейзи": "DayZ",
    "dayz": "DayZ",
    "дарктайд": "Warhammer 40,000: Darktide",
    "darktide": "Warhammer 40,000: Darktide",
    "ремнант": "Remnant II",
    "remnant 2": "Remnant II",
    "аутласт": "Outlast",
    "outlast": "Outlast",
    "гоствайр": "Ghostwire: Tokyo",
    "ghostwire": "Ghostwire: Tokyo",
    "hifi rush": "Hi-Fi RUSH",
    "хай фай": "Hi-Fi RUSH",
    "якуза": "Like a Dragon: Infinite Wealth",
    "yakuza": "Like a Dragon: Infinite Wealth",
    "like a dragon": "Like a Dragon: Infinite Wealth",
    "ffxiv": "FINAL FANTASY XIV Online",
    "фф14": "FINAL FANTASY XIV Online",
    "final fantasy 14": "FINAL FANTASY XIV Online",
    "геншин": "Genshin Impact",
    "genshin": "Genshin Impact",
    "хонкай": "Honkai: Star Rail",
    "honkai": "Honkai: Star Rail",
    "hsr": "Honkai: Star Rail",
    "майнкрафт": "Minecraft",
    "minecraft": "Minecraft",
    "майн": "Minecraft",
    "роблокс": "Roblox",
    "roblox": "Roblox",
    "айзек": "The Binding of Isaac: Rebirth",
    "binding of isaac": "The Binding of Isaac: Rebirth",
    "тбои": "The Binding of Isaac: Rebirth",
    "диско": "Disco Elysium - The Final Cut",
    "disco elysium": "Disco Elysium - The Final Cut",
    "аутер вайлдс": "Outer Wilds",
    "outer wilds": "Outer Wilds",
    "сабнатика бз": "Subnautica: Below Zero",
    "below zero": "Subnautica: Below Zero",
    "underlords": "Dota Underlords",
    "андерлордс": "Dota Underlords",
    "артефакт": "Artifact",
    "artifact": "Artifact",
    "хеллдайверс": "HELLDIVERS™ 2",
    "хеллдайверс 2": "HELLDIVERS™ 2",
    "helldivers": "HELLDIVERS™ 2",
    "helldivers 2": "HELLDIVERS™ 2",
    "хелл дайверс": "HELLDIVERS™ 2",
    "нарка": "NARAKA: BLADEPOINT",
    "naraka": "NARAKA: BLADEPOINT",
    "нарка блейдпоинт": "NARAKA: BLADEPOINT",
    "гусь гусь утка": "Goose Goose Duck",
    "goose goose duck": "Goose Goose Duck",
    "ггд": "Goose Goose Duck",
    "обои движ": "Wallpaper Engine",
    "wallpaper engine": "Wallpaper Engine",
    "впе": "Wallpaper Engine",
    "арк рейдерс": "ARC Raiders",
    "arc raiders": "ARC Raiders",
    "поэ 2": "Path of Exile 2",
    "poe2": "Path of Exile 2",
    "path of exile 2": "Path of Exile 2",
    "патч 2": "Path of Exile 2",
    "мх вайлдс": "Monster Hunter Wilds",
    "mhwilds": "Monster Hunter Wilds",
    "monster hunter wilds": "Monster Hunter Wilds",
    "марвел ривалс": "Marvel Rivals",
    "marvel rivals": "Marvel Rivals",
    "ванс хьюман": "Once Human",
    "once human": "Once Human",
    "саундпад": "Soundpad",
    "soundpad": "Soundpad",
    "чейнд тугезер": "Chained Together",
    "chained together": "Chained Together",
    "сити скайлайнс 2": "Cities: Skylines II",
    "cities skylines 2": "Cities: Skylines II",
    "банана": "Banana",
    "banana": "Banana",
    "сталкер сердце": "S.T.A.L.K.E.R. 2: Heart of Chornobyl",
    "stalker heart": "S.T.A.L.K.E.R. 2: Heart of Chornobyl",
    "харт оф чернобыль": "S.T.A.L.K.E.R. 2: Heart of Chornobyl",
    "скайрим се": "The Elder Scrolls V: Skyrim Special Edition",
    "skyrim se": "The Elder Scrolls V: Skyrim Special Edition",
    "скайрим спешл": "The Elder Scrolls V: Skyrim Special Edition",
    "скайрим легендари": "The Elder Scrolls V: Skyrim Legendary Edition",
    "skyrim legendary": "The Elder Scrolls V: Skyrim Legendary Edition",
    "скайрим вр": "The Elder Scrolls V: Skyrim VR",
    "skyrim vr": "The Elder Scrolls V: Skyrim VR",
    "фм 25": "Football Manager 2025",
    "fm25": "Football Manager 2025",
    "football manager 2025": "Football Manager 2025",
    "nba 2k25": "NBA 2K25",
    "нба 2к25": "NBA 2K25",
    "мк1": "Mortal Kombat 1",
    "mk1": "Mortal Kombat 1",
    "mortal kombat 1": "Mortal Kombat 1",
    "фк 25": "EA SPORTS FC™ 25",
    "fc25": "EA SPORTS FC™ 25",
    "fc 25": "EA SPORTS FC™ 25",
    "еа фк": "EA SPORTS FC™ 25",
    "фифа 25": "EA SPORTS FC™ 25",
    "arma reforger": "Arma Reforger",
    "арма рефоргер": "Arma Reforger",
    "eu5": "Europa Universalis V",
    "ев5": "Europa Universalis V",
    "европа 5": "Europa Universalis V",
    "цив 7": "Sid Meier's Civilization VII",
    "civ 7": "Sid Meier's Civilization VII",
    "civ7": "Sid Meier's Civilization VII",
    "цивилизация 7": "Sid Meier's Civilization VII",
    "дивинити 2": "Divinity: Original Sin 2",
    "divinity 2": "Divinity: Original Sin 2",
    "dos2": "Divinity: Original Sin 2",
    "дос2": "Divinity: Original Sin 2",
    "dying light 2": "Dying Light 2 Stay Human®",
    "дайинг лайт 2": "Dying Light 2 Stay Human®",
    "dl2": "Dying Light 2 Stay Human®",
    "хогвартс легаси": "Hogwarts Legacy",
    "hogwarts legacy": "Hogwarts Legacy",
    "star citizen": "Star Citizen",
    "стар ситизен": "Star Citizen",
    "скайфорж": "Skyforge",
    "skyforge": "Skyforge",
    "lost light": "Lost Light",
    "лост лайт": "Lost Light",
    "world of warships": "World of Warships",
    "вовшипс": "World of Warships",
    "wows": "World of Warships",
    "world of tanks": "World of Tanks",
    "wot": "World of Tanks",
    "вот танкс": "World of Tanks",
    "wot blitz": "World of Tanks Blitz",
    "wotb": "World of Tanks Blitz",
    "crossout": "Crossout",
    "кроссаут": "Crossout",
    "enlisted": "Enlisted",
    "энлистед": "Enlisted",
    "neverwinter": "Neverwinter",
    "невервинтер": "Neverwinter",
    "eve online": "EVE Online",
    "ив онлайн": "EVE Online",
    "eve": "EVE Online",
    "albion": "Albion Online",
    "альбион": "Albion Online",
    "albion online": "Albion Online",
    "black desert": "Black Desert",
    "бдо": "Black Desert",
    "bdo": "Black Desert",
    "tera": "TERA",
    "тера": "TERA",
    "blade and soul": "Blade & Soul NEO",
    "бнс": "Blade & Soul NEO",
    "bns": "Blade & Soul NEO",
    "throne and liberty": "THRONE AND LIBERTY",
    "трон энд либерти": "THRONE AND LIBERTY",
    "where winds meet": "Where Winds Meet",
    "виндс мит": "Where Winds Meet",
    "wuthering waves": "Wuthering Waves",
    "вув": "Wuthering Waves",
    "wuwa": "Wuthering Waves",
    "zenless zone zero": "Zenless Zone Zero",
    "zzz": "Zenless Zone Zero",
    "ззз": "Zenless Zone Zero",
    "zenless": "Zenless Zone Zero",
    "delta force": "Delta Force",
    "дельта форс": "Delta Force",
    "df hawk": "Delta Force",
    "the finals": "THE FINALS",
    "файналс": "THE FINALS",
    "finals": "THE FINALS",
    "splitgate 2": "Splitgate 2",
    "сплитгейт 2": "Splitgate 2",
    "the first descendant": "The First Descendant",
    "тфд": "The First Descendant",
    "tfd": "The First Descendant",
    "first descendant": "The First Descendant",
    "warhammer 40k darktide": "Warhammer 40,000: Darktide",
    "space marine 2": "Warhammer 40,000: Space Marine 2",
    "спейс марин 2": "Warhammer 40,000: Space Marine 2",
    "sm2": "Warhammer 40,000: Space Marine 2",
}


def list_known_game_titles() -> list[str]:
    return sorted({v for v in GAME_ALIASES.values()}, key=str.casefold)


def sort_game_names(games: list) -> list:
    return sorted(games, key=str.casefold)


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(cfg: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def resolve_vanity_url(
    api_key: str, vanity: str, log_fn: LogFn = None
) -> Optional[str]:
    url = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/"
    params = {"key": api_key, "vanityurl": vanity}
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    except Exception as e:
        _log(log_fn, f"  Запрос ResolveVanityURL: {type(e).__name__}: {e}", "err")
        return None

    if resp.status_code != 200:
        _log(log_fn, f"  Ошибка {resp.status_code} при ResolveVanityURL", "err")
        _log(log_fn, f"  Ответ: {resp.text[:300]}", "warn")
        return None

    try:
        data = resp.json()
        response = data.get("response", {})
        if response.get("success") == 1:
            return str(response["steamid"])
        msg = response.get("message", "неизвестно")
        _log(log_fn, f"  Steam не нашёл профиль '{vanity}': {msg}", "err")
        return None
    except Exception as e:
        _log(log_fn, f"  Разбор JSON: {e}", "err")
        _log(log_fn, f"  Ответ: {resp.text[:300]}", "warn")
        return None


def parse_account_to_steamid64(
    api_key: str, account_input: str, log_fn: LogFn = None
) -> Optional[str]:
    s = account_input.strip().rstrip("/")

    if re.fullmatch(r"\d{17}", s):
        return s

    m = re.search(r"steamcommunity\.com/profiles/(\d{17})", s)
    if m:
        return m.group(1)

    m = re.search(r"steamcommunity\.com/id/([^/?#]+)", s)
    if m:
        vanity = m.group(1)
        _log(log_fn, f"  Определяем профиль для vanity '{vanity}'...", "warn")
        return resolve_vanity_url(api_key, vanity, log_fn)

    _log(log_fn, f"  Определяем профиль для nickname '{s}'...", "warn")
    return resolve_vanity_url(api_key, s, log_fn)


def fetch_persona_name(
    api_key: str, steamid64: str, log_fn: LogFn = None
) -> str:
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    params = {"key": api_key, "steamids": steamid64}
    _log(log_fn, "  Запрос отображаемого имени профиля…", "dim")
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=20)
    except Exception:
        return ""
    if resp.status_code != 200:
        return ""
    try:
        data = resp.json()
    except Exception:
        return ""
    players = data.get("response", {}).get("players") or []
    if not players:
        return ""
    name = players[0].get("personaname")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return ""


def fetch_owned_games(
    api_key: str, steamid64: str, log_fn: LogFn = None
) -> Optional[list]:
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": api_key,
        "steamid": steamid64,
        "include_appinfo": 1,
        "include_played_free_games": 1,
        "format": "json",
    }

    _log(log_fn, "  Запрос списка игр библиотеки…", "dim")

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
    except requests.exceptions.ConnectionError as e:
        _log(log_fn, "  Нет подключения к интернету!", "err")
        _log(log_fn, f"  Детали: {e}", "err")
        return None
    except requests.exceptions.Timeout:
        _log(log_fn, "  Таймаут запроса (30с)", "err")
        return None
    except Exception as e:
        _log(log_fn, f"  {type(e).__name__}: {e}", "err")
        return None

    if resp.status_code == 401:
        _log(log_fn, "  Неверный API ключ!", "err")
        _log(log_fn, "  Проверь ключ в настройках или в config.json.", "warn")
        return None

    if resp.status_code == 403:
        _log(log_fn, "  Доступ запрещён.", "err")
        _log(log_fn, "  Профиль закрыт или API ключ не валиден.", "warn")
        return None

    if resp.status_code == 429:
        _log(log_fn, "  Слишком много запросов — Steam заблокировал.", "err")
        _log(log_fn, "  Повысьте задержку между запросами в настройках.", "warn")
        return None

    if resp.status_code != 200:
        _log(log_fn, f"  Статус: {resp.status_code}", "err")
        _log(log_fn, f"  Ответ: {resp.text[:500]}", "warn")
        return None

    try:
        data = resp.json()
    except Exception as e:
        _log(log_fn, f"  Не удалось разобрать JSON: {e}", "err")
        _log(log_fn, f"  Ответ: {resp.text[:500]}", "warn")
        return None

    response = data.get("response", {})

    if not response:
        _log(log_fn, "  Пустой ответ от Steam.", "err")
        _log(log_fn, "  Скорее всего профиль закрыт (приватный).", "warn")
        _log(
            log_fn,
            "  Попросите владельца открыть профиль, изменить его и сделать список игр открытым.",
            "warn",
        )
        return None

    game_count = response.get("game_count", 0)
    games_raw = response.get("games", [])

    if game_count == 0 or not games_raw:
        _log(log_fn, "  На аккаунте 0 игр или список скрыт.", "warn")
        return []

    games = []
    for g in games_raw:
        games.append(
            {
                "name": g.get("name", f"AppID:{g.get('appid', '?')}"),
                "appid": str(g.get("appid", "?")),
                "playtime": g.get("playtime_forever", 0),
            }
        )

    return games


def find_game(target: str, games: list) -> Optional[dict]:
    t_lower = target.lower().strip()

    for g in games:
        if g["name"].lower().strip() == t_lower:
            return g

    return None


def resolve_game_name(raw: str, log_fn: LogFn = None) -> str:
    key = raw.strip().lower()
    if key in GAME_ALIASES:
        resolved = GAME_ALIASES[key]
        _log(log_fn, f"  Псевдоним '{raw}' -> '{resolved}'", "warn")
        return resolved
    return raw.strip()


def sanitize_name(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "_", name).strip()


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def format_account_result_line(account_raw: str, persona_name: str) -> str:
    raw = account_raw.strip()
    nick = (persona_name or "").strip()
    if nick:
        return f"{raw}  |  {nick}"
    return raw


def save_result(
    game_name: str, account_raw: str, has_game: bool, persona_name: str = ""
) -> None:
    folder = os.path.join(OUTPUT_DIR, sanitize_name(game_name))
    ensure_dir(folder)

    filename = "found.txt" if has_game else "not_found.txt"
    filepath = os.path.join(folder, filename)

    line = format_account_result_line(account_raw, persona_name) + "\n"

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(line)


def save_profile_checked_games(
    steamid64: str,
    account_raw: str,
    owned_from_checklist: list[str],
    persona_name: str = "",
) -> None:
    ensure_dir(PROFILES_DIR)
    path = os.path.join(PROFILES_DIR, f"{steamid64}.txt")
    head = format_account_result_line(account_raw, persona_name)
    body = [head, ""] + sort_game_names(owned_from_checklist)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(body) + "\n")


def load_accounts_from_file(filepath: str) -> list:
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f]
    return [l for l in lines if l and not l.startswith("#")]


def progress_bar(cur: int, total: int, width: int = 44) -> str:
    if total == 0:
        return "[" + "-" * width + "] --%"
    filled = int(width * cur / total)
    bar = "=" * filled + "." * (width - filled)
    pct = int(100 * cur / total)
    return f"[{bar}] {pct}% ({cur}/{total})"


def run_check(
    api_key: str,
    accounts: list,
    games: list,
    log_fn: LogFn = None,
    request_delay: float = None,
) -> list:
    delay = request_delay if request_delay is not None else REQUEST_DELAY
    games_run = sort_game_names(games)

    _log(log_fn, "\n" + "=" * 58, "title")
    _log(log_fn, "  НАЧИНАЕМ ПРОВЕРКУ", "title")
    _log(log_fn, "=" * 58, "title")
    _log(log_fn, f"  Аккаунтов : {len(accounts)}", "info")
    _log(log_fn, f"  Игр       : {len(games)}", "info")
    _log(log_fn, f"  Задержка  : {delay}с", "info")
    _log(log_fn, "=" * 58, "title")

    ensure_dir(OUTPUT_DIR)
    ensure_dir(PROFILES_DIR)

    total = len(accounts)
    summary = []

    for idx, account_raw in enumerate(accounts, 1):
        _log(log_fn, f"\n{'─' * 58}", "dim")
        _log(log_fn, f"  [{idx}/{total}] {account_raw}", "title")
        _log(log_fn, "  " + progress_bar(idx - 1, total), "info")
        _log(log_fn, f"{'─' * 58}", "dim")

        steamid = parse_account_to_steamid64(api_key, account_raw, log_fn)

        if not steamid:
            _log(log_fn, "  Не удалось определить профиль Steam — пропускаем.", "err")
            for game in games_run:
                summary.append(
                    (account_raw, "?", game, "ERROR", 0)
                )
                save_result(game, account_raw, False)
            if idx < total:
                time.sleep(delay)
            continue

        _log(log_fn, "  Профиль определён.", "ok")

        time.sleep(delay)
        persona = fetch_persona_name(api_key, steamid, log_fn)
        if persona:
            _log(log_fn, f'  Ник в Steam: "{persona}"', "dim")
        time.sleep(delay)
        games_list = fetch_owned_games(api_key, steamid, log_fn)

        if games_list is None:
            _log(log_fn, "  Не удалось получить список игр.", "err")
            for game in games_run:
                summary.append(
                    (account_raw, steamid, game, "ERROR", 0)
                )
                save_result(game, account_raw, False, persona)
            if idx < total:
                time.sleep(delay)
            continue

        _log(log_fn, f"  Игр в библиотеке: {len(games_list)}", "ok")
        _log(log_fn, "", "info")

        owned_from_checklist: list[str] = []
        for game in games_run:
            found = find_game(game, games_list)

            if found:
                playtime = found.get("playtime", 0)
                owned_from_checklist.append(game)
                _log(log_fn, f'  Есть "{game}"', "ok")
                summary.append((account_raw, steamid, game, "FOUND", playtime))
                save_result(game, account_raw, True, persona)
            else:
                _log(log_fn, f'  Нет "{game}"', "err")
                summary.append((account_raw, steamid, game, "MISSING", 0))
                save_result(game, account_raw, False, persona)

        save_profile_checked_games(steamid, account_raw, owned_from_checklist, persona)

        if idx < total:
            _log(log_fn, f"\n  Ждём {delay}с...", "dim")
            time.sleep(delay)

    _log(log_fn, "\n  " + progress_bar(total, total), "info")
    return summary


def create_accounts_template() -> None:
    if not os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            f.write("")
