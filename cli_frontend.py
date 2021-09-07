"""A command-line frontend for http_backend.py."""

import json
import time

import requests


def get_prefix(text, prefix):
    """If a text string starts with a substring, return the substring and the text minus the first instance of the
    substring; otherwise return None and the text.
    """
    if text.startswith(prefix):
        return prefix, text[len(prefix):].lstrip()
    return None, text


def main():
    """Main method to start the bot."""

    with open("config.json") as config_file:
        config = json.load(config_file)

    prefix = config.get("prefix", "")
    backend_port_number = config.get("backend_port_number", 9980)
    backend_url = f"http://localhost:{backend_port_number}"

    print(f"Running on port {backend_port_number}")
    print("Enter commands here.", end="")
    if prefix:
        print(f" Commands must start with {prefix}")
    else:
        print()
    prefix_space = " " if prefix and prefix[-1].isalnum() else ""
    print(f"For help, type {prefix}{prefix_space}help")

    while True:
        prefix, message = get_prefix(input("> "), prefix)
        if not prefix:
            continue
        try:
            response = requests.post(backend_url, json={
                "id": f"cli:{time.time()}",
                "message": message,
                "is_owner": True,
                "character_limit": 0
            })
            replies = response.json()
            for reply in replies:
                print(reply)
        except Exception:
            print("Error: http_backend.py is not running!")


if __name__ == "__main__":
    main()
