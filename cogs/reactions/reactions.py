"""Generic reaction image commands."""

import json
import secrets

from sailor import commands


def setup(processor):
    """Set up reaction commands."""

    with open("reactions.json") as file_object:
        reactions = json.load(file_object)

    async def coro(event):
        """Generic coroutine."""
        properties = reactions.get(event.command.name)
        message = properties.get("message")
        if message:
            await event.reply(message)
        images = properties.get("images")
        if images:
            image = secrets.choice(images)
            await event.reply(image)

    for command_name, command_properties in reactions.items():
        aliases = command_properties.get("aliases", [])
        new_command = commands.Command(coro, name=command_name, aliases=aliases)
        new_command.help = f"Posts a {command_name}-themed image."
        processor.add_command(new_command)
