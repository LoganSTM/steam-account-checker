# Steam Game Checker

Desktop and CLI utility for checking whether Steam accounts own specific games through the Steam Web API.

## Features

- PyQt6 desktop interface
- CLI mode for terminal usage
- Support for nicknames, profile URLs, and `SteamID64`
- Steam store search in the GUI
- Game alias resolution for common shorthand names
- Export of results into text files

## Project Structure

- `steam_checker_app.py` - GUI application
- `steam_checker.py` - CLI application
- `steam_core.py` - shared core logic
- `steam_checker_app.spec` - PyInstaller build spec
- `accounts.txt` - input template for Steam accounts
- `config.example.json` - example local config

## Requirements

- Python 3.11+
- Windows is the main target for the GUI build

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a local `config.json` based on `config.example.json`:

```json
{
  "api_key": "YOUR_STEAM_WEB_API_KEY"
}
```

The real `config.json` is ignored by Git and should stay local.

## Getting a Steam Web API Key

1. Open `https://steamcommunity.com/dev/apikey`
2. Sign in with your Steam account
3. Enter any domain name, for example `localhost`
4. Copy the generated key

## GUI Usage

Run:

```bash
python steam_checker_app.py
```

In the app you can:

- save your Steam Web API key
- add games manually or through Steam store search
- paste accounts directly or load them from `accounts.txt`
- run the check and inspect the log

## CLI Usage

Run:

```bash
python steam_checker.py
```

The CLI lets you:

- save or change the API key
- enter games and accounts interactively
- run the same ownership check as the GUI

## Output

Results are written into `steam_results/` and grouped by game:

- `found.txt`
- `not_found.txt`
- `profiles/<steamid>.txt`

This output directory is ignored by Git.

## Build EXE

```bash
pyinstaller steam_checker_app.spec
```

## Notes

- `accounts.txt` is safe to keep as a template, but avoid committing real private account lists.
- `config.json`, build artifacts, caches, and result files are excluded through `.gitignore`.
- No authentication, license checks, or bundled secrets are required to run the project.

