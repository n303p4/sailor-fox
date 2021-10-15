"""Generic reaction image commands."""

import json
import secrets

from sailor import commands


def setup(processor):
    """Set up reaction commands."""

    with open("reactions.json") as file_object:
        reactions = json.load(file_object)

    last_image_for_command = {}

    async def coro(event):
        """Generic coroutine."""
        command_properties = reactions.get(event.command.name)
        message = command_properties.get("message")
        if message:
            await event.reply(message)
        images = command_properties.get("images")
        if not isinstance(images, list):
            return
        # Avoid repeats when possible
        image = secrets.choice(images)
        while image == last_image_for_command.get(event.command.name):
            image = secrets.choice(images)
        if len(images) > 1:
            last_image_for_command[event.command.name] = image
        await event.reply(image)

    for command_name, command_properties in reactions.items():
        aliases = command_properties.get("aliases", [])
        new_command = commands.Command(coro, name=command_name, aliases=aliases)
        new_command.help = f"Posts a {command_name}-themed image."
        processor.add_command(new_command)
