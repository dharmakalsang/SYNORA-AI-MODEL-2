"""Authentication and account storage helpers."""

import json
from pathlib import Path

ACCOUNTS_PATH = Path(__file__).resolve().parent.parent / "accounts.json"
DEFAULT_ACCOUNTS = {
    "users": {
        "dhrmakalsang@gmail.com": {
            "password": "kalsangong1234",
            "history": [
                "Default account created.",
                "This account has its own history stored locally."
            ]
        }
    }
}


def ensure_accounts_file() -> None:
    if not ACCOUNTS_PATH.exists():
        save_accounts(DEFAULT_ACCOUNTS)


def load_accounts() -> dict:
    if not ACCOUNTS_PATH.exists():
        save_accounts(DEFAULT_ACCOUNTS)
    try:
        with open(ACCOUNTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        save_accounts(DEFAULT_ACCOUNTS)
        return DEFAULT_ACCOUNTS.copy()


def save_accounts(accounts: dict) -> None:
    with open(ACCOUNTS_PATH, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=2)


def authenticate(email: str, password: str) -> bool:
    accounts = load_accounts()
    user = accounts.get("users", {}).get(email)
    return bool(user and user.get("password") == password)


def create_account(email: str, password: str) -> bool:
    accounts = load_accounts()
    if email in accounts.get("users", {}):
        return False
    accounts.setdefault("users", {})[email] = {
        "password": password,
        "history": ["Account created."]
    }
    save_accounts(accounts)
    return True


def add_history(email: str, text: str) -> None:
    accounts = load_accounts()
    user = accounts.get("users", {}).get(email)
    if not user:
        return
    user.setdefault("history", []).append(text)
    save_accounts(accounts)


def get_history(email: str) -> list:
    accounts = load_accounts()
    user = accounts.get("users", {}).get(email)
    return user.get("history", []) if user else []
