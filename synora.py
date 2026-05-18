#!/usr/bin/env python3
"""
SYNORA AI System - Main Entry Point

This file integrates:
- Synora AI (via Ollama gemma4)
- Communication tools (Telegram, Discord, WhatsApp, etc.)
- Camera tools
- Command parsing and natural language processing
- Local account login and history tracking

Warning: Requires 'ollama pull gemma4' to be run first
"""

import json
import os
import subprocess
import sys
import time
from getpass import getpass

# Import local tools
import Tools_script.search_engine as search_engine
import Tools_script.synora_comm as synora_comm
import Tools_script.camera_tool as camera_tool
import Tools_script.voice_assistant as voice_assistant
import Tools_script.file_control as file_control
import Tools_script.todo_reminder as todo_reminder
import Tools_script.atdef as atdef


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_PATH = os.path.join(BASE_DIR, "accounts.json")
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
    if not os.path.exists(ACCOUNTS_PATH):
        with open(ACCOUNTS_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_ACCOUNTS, f, indent=2)


def load_accounts() -> dict:
    with open(ACCOUNTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


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


def login_menu() -> str:
    ensure_accounts_file()
    while True:
        choice = input("Type [L]ogin or [C]reate account: ").strip().lower()
        if choice in ("l", "login"):
            email = input("Email: ").strip()
            password = getpass("Password: ")
            if authenticate(email, password):
                print("Login successful.")
                return email
            print("Wrong email or password. Wait 10 seconds and try again.")
            time.sleep(10)
            continue

        if choice in ("c", "create", "new"):
            email = input("New email: ").strip()
            if not email:
                print("Email cannot be empty.")
                continue
            password = getpass("New password: ")
            confirm = getpass("Confirm password: ")
            if password != confirm:
                print("Passwords do not match.")
                continue
            if create_account(email, password):
                print("Account created successfully. You can now log in.")
                continue
            print("This email already exists.")
            continue

        print("Please enter L for login or C to create a new account.")


def main_menu() -> str:
    """Display main menu for user to choose actions."""
    print("\n" + "=" * 30)
    print("SYNORA AI System")
    print("=" * 30)
    print("1. Chat with Synora AI (search fallback)")
    print("2. Send a message")
    print("3. Open a website")
    print("4. Access camera")
    print("5. Execute custom command")
    print("6. Show history")
    print("7. Exit")
    print("=" * 30)
    return input("Choose an option (1-7): ").strip()


def run_synora_ai() -> None:
    """Run Synora AI for interactive chat."""
    try:
        subprocess.run(["ollama", "run", "gemma4"])
    except FileNotFoundError:
        print("Error: 'ollama' command not found. Install Ollama and run 'ollama pull gemma4'")
    except KeyboardInterrupt:
        print("\nExited by user.")


def chat_with_search() -> None:
    """Run a chat loop that falls back to Google search when needed."""
    print("\n--- Synora AI Chat Mode (with Google fallback) ---")
    print("Type your question or 'quit' to exit\n")
    while True:
        question = input("Ask Synora: ").strip()
        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            break
        synora_comm.handle_synora_request(question)


def main() -> None:
    """Main entry point for Synora system."""
    user_email = login_menu()
    print(f"Welcome, {user_email}! Your account history is stored locally.")

    while True:
        try:
            choice = main_menu()

            if choice == "1":
                chat_with_search()

            elif choice == "2":
                print("\nExample commands:")
                print("  - tell alice to say hello to bob")
                print("  - ask john to say good morning to sarah")
                command = input("\nEnter command: ")
                synora_comm.execute_command(command)
                add_history(user_email, f"Message command: {command}")

            elif choice == "3":
                url = input("Enter URL to open (e.g., google.com): ").strip()
                synora_comm.open_browser_url(url)
                print(f"Opening: {url}")
                add_history(user_email, f"Opened URL: {url}")

            elif choice == "4":
                print("\nOpening camera...")
                print("Press 'q' to quit, 's' to save photo")
                camera_tool.main()
                add_history(user_email, "Accessed camera")

            elif choice == "5":
                print("\nExample: 'open youtube.com and tell alice say hello to bob'")
                request = input("Enter your request: ")
                synora_comm.handle_synora_request(request)
                add_history(user_email, f"Request: {request}")

            elif choice == "6":
                history = get_history(user_email)
                if not history:
                    print("No history yet.")
                else:
                    print("--- Your account history ---")
                    for index, item in enumerate(history, start=1):
                        print(f"{index}. {item}")

            elif choice == "7":
                print(f"\nGoodbye, {user_email}!")
                break

            else:
                print("Invalid option, please try again.")

        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()
