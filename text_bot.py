#!/usr/bin/env python3

"""A basic command-line bot made using sailor's command handler."""

import asyncio
import os
import sys

from sailor import commands

loop = asyncio.get_event_loop()
processor = commands.Processor(loop=loop, prefix="sf", logout=sys.exit)


async def send(message):
    """Here is a very basic send coroutine, for a text bot."""
    print(message)


def main():
    """Main method called from a run_until_complete() or similar."""
    print(f"Enter commands here. Commands must start with {processor.prefix}")
    print(f"For help, use {processor.prefix} help.")
    while 1:
        message = input("> ")
        try:
            processor.process_sync(message, is_owner=True, callback_send=send)
        except:
            pass

if __name__ == "__main__":
    # Automatically load all modules.
    processor.load_config()
    blacklist = processor.config.get("module_blacklist", [])
    processor.add_modules_from_dir("cogs", blacklist=blacklist)
    main()
