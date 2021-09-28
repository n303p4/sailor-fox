"""A command-line frontend for http_backend.py."""

# pylint: disable=broad-except

import json
import time

import requests

from sailor_fox.helpers import get_prefix


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
        message = input("> ")
        if not message:
            continue
        prefix_or_none, message = get_prefix(message, prefix)
        if prefix_or_none is None or not message:
            continue
        try:
            response = requests.post(backend_url, json={
                "id": f"cli.py:{time.time()}",
                "message": message,
                "is_owner": True,
                "character_limit": 0
            })
            action_stack = response.json()
            for action in action_stack:
                print(action.get("value"))
        except Exception:
            print("Error: http_backend.py is not running!")


if __name__ == "__main__":
    main()
