"""Example communication access and Synora AI connector.

This file shows:
- standard library imports
- third-party imports
- basic communication app access
- a local AI connector via Ollama / Synora
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import webbrowser

import Tools_script.search_engine as search_engine

# Third-party imports
# These are not part of Python by default and need installation.
try:
    import requests
except ImportError:
    requests = None


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> dict:
    """Send a Telegram message using the Bot API."""
    if requests is None:
        raise RuntimeError("Please install requests: pip install requests")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


def send_discord_webhook(webhook_url: str, content: str) -> dict:
    """Send a message to Discord using a webhook."""
    if requests is None:
        raise RuntimeError("Please install requests: pip install requests")

    payload = {"content": content}
    response = requests.post(webhook_url, json=payload, timeout=15)
    response.raise_for_status()
    return response.json() if response.text else {"status": "sent"}


def open_whatsapp_web(phone_number: str, message: str) -> None:
    """Open WhatsApp Web in the browser with a pre-filled message."""
    encoded = urllib.parse.quote(message)
    url = f"https://api.whatsapp.com/send?phone={phone_number}&text={encoded}"
    webbrowser.open(url, new=2)


def open_browser_url(url: str) -> None:
    """Open a URL using the system web browser."""
    webbrowser.open(url, new=2)


def connect_synora_ai(prompt: str, model: str = "gemma4") -> str:
    """Run Synora AI via Ollama if installed locally and return output."""
    try:
        proc = subprocess.run(
            ["ollama", "run", model, "--prompt", prompt],
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout.strip()
    except FileNotFoundError:
        print("Error: Ollama is not installed or not in PATH.")
        return ""
    except subprocess.CalledProcessError as exc:
        print(f"Synora AI returned an error: {exc}")
        return ""


def synthesize_answer_with_search(query: str, num_results: int = 3) -> str:
    """Use Google results to enrich an AI answer when the model needs extra data."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    cx = os.environ.get("GOOGLE_CX")

    print("Searching Google for additional information...")
    results = search_engine.google_search(query, api_key=api_key, cx=cx, num=num_results)
    if not results:
        return ""

    lines = []
    for index, item in enumerate(results, start=1):
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        link = item.get("link", "")
        lines.append(f"{index}. {title}\n{snippet}\n{link}")

    search_text = "\n\n".join(lines)
    prompt = (
        f"The user asked: {query}\n\n"
        "Use the following search results to write a clear, natural answer: \n\n"
        f"{search_text}\n\n"
        "Answer in one or two sentences using the information above."
    )
    return connect_synora_ai(prompt)


def is_unknown_response(response: str) -> bool:
    """Determine if the AI response indicates a lack of knowledge."""
    if not response:
        return True
    unknown_phrases = [
        "i don't know",
        "i am not sure",
        "i'm not sure",
        "i cannot",
        "i cannot answer",
        "unable to",
        "as an ai",
        "no information",
        "sorry",
        "cannot find",
    ]
    normalized = response.lower()
    return any(phrase in normalized for phrase in unknown_phrases)


def clean_command(command: str) -> str:
    """Return a normalized command string for parsing."""
    return re.sub(r"[\s\t\n]+", " ", command.lower().strip())


def parse_command(command: str) -> dict:
    """Parse a natural command string for open and tell actions."""
    command = clean_command(command)

    result = {
        "open_url": None,
        "message_action": None,
        "message_target": None,
        "message_text": None,
        "message_action_to": None,
    }

    # Simple open URL detection
    open_match = re.search(
        r"(?:open|go to|visit|launch|show) (https?://\S+|www\.\S+|\S+\.(?:com|net|org|id|io|xyz|app|site))",
        command,
    )
    if open_match:
        url = open_match.group(1)
        if not url.startswith("http"):
            url = "https://" + url
        result["open_url"] = url

    # Natural 'tell' patterns
    patterns = [
        r"tell (?P<target>[\w\s]+?) to say (?P<text>.+?) to (?P<recipient>[\w\s]+)$",
        r"ask (?P<target>[\w\s]+?) to say (?P<text>.+?) to (?P<recipient>[\w\s]+)$",
        r"ask (?P<target>[\w\s]+?) to tell (?P<recipient>[\w\s]+?) (?P<text>.+)$",
        r"send (?P<target>[\w\s]+?) message (?P<text>.+?) to (?P<recipient>[\w\s]+)$",
        r"tell (?P<target>[\w\s]+?) (?P<text>.+?) to (?P<recipient>[\w\s]+)$",
    ]

    for pattern in patterns:
        match = re.search(pattern, command)
        if match:
            result["message_action"] = "tell_person"
            result["message_target"] = match.group("target").strip()
            result["message_text"] = match.group("text").strip(" .!? ")
            result["message_action_to"] = match.group("recipient").strip()
            break

    return result


def execute_command(command: str) -> None:
    """Execute parsed commands: open URL and send message notifications."""
    parsed = parse_command(command)

    if parsed["open_url"]:
        print(f"Opening URL: {parsed['open_url']}")
        open_browser_url(parsed["open_url"])

    if parsed["message_action"] == "tell_person":
        target = parsed.get("message_target")
        text = parsed.get("message_text")
        action_to = parsed.get("message_action_to")

        print(f"Preparing to tell {target} to say '{text}' to {action_to}.")

        # Example contact mapping: update these values with real credentials
        contacts = {
            "alice": {
                "type": "telegram",
                "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
                "chat_id": "YOUR_TELEGRAM_CHAT_ID",
            },
            "bob": {
                "type": "discord",
                "webhook_url": "YOUR_DISCORD_WEBHOOK_URL",
            },
        }

        contact = contacts.get(target.lower())
        if not contact:
            print(f"No contact configuration found for '{target}'.")
            return

        message = f"{action_to}, {target} says: {text}"

        if contact["type"] == "telegram":
            send_telegram_message(contact["bot_token"], contact["chat_id"], message)
            print("Telegram message sent.")
        elif contact["type"] == "discord":
            send_discord_webhook(contact["webhook_url"], message)
            print("Discord message dispatched.")
        else:
            print(f"Unknown contact type for {target}: {contact['type']}")


def handle_synora_request(request_text: str) -> None:
    """Handle a natural Synora request, executing commands or falling back to AI and Google search."""
    request_text = request_text.strip()
    parsed = parse_command(request_text)

    if parsed["open_url"] or parsed["message_action"]:
        execute_command(request_text)
        return

    print("Sending request to Synora AI...")
    ai_response = connect_synora_ai(request_text)
    if is_unknown_response(ai_response):
        print("AI appears uncertain. Falling back to Google search...")
        search_response = synthesize_answer_with_search(request_text)
        if search_response:
            print(search_response)
            return
        print("Search fallback could not retrieve structured results. Opening browser search instead.")
        search_engine.google_search(request_text)
        return

    print(ai_response)


def demo() -> None:
    """Demo showing how the imports and connection functions work."""
    print("--- Communication and Synora AI Demo ---")

    # Standard library import example
    print("1) Standard library import: webbrowser, subprocess, urllib.parse")
    open_browser_url("https://www.google.com")

    # Third-party import example
    if requests is not None:
        print("2) Third-party import available: requests")
    else:
        print("2) Third-party import missing: install requests")

    # Example usage for Telegram / Discord / WhatsApp
    print("3) You can call send_telegram_message, send_discord_webhook, open_whatsapp_web")
    print("   Replace bot_token/chat_id/webhook_url with your actual values.")

    # Synora AI connection example
    connect_synora_ai("Hello Synora, this is a test prompt.")


if __name__ == "__main__":
    demo()
