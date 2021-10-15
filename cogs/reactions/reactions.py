"""Generic reaction image commands."""

import json
import secrets

from sailor import commands
from sailor.exceptions import UserInputError


def setup(processor):
    """Set up reaction commands."""

    with open("reactions.json") as file_object:
        reactions = json.load(file_object)

    last_image_for_command = {}

    async def coro(event, image_number: int = None):
        """Generic coroutine."""
        command_properties = reactions.get(event.command.name)
        message = command_properties.get("message")
        if message:
            await event.reply(message)
        images = command_properties.get("images")
        if not isinstance(images, list):
            return
        # Avoid repeats when possible
        if len(images) > 1 and isinstance(image_number, int):
            image_number -= 1
            if image_number not in range(len(images)):
                raise UserInputError(f"Number must be from 1 to {len(images)}")
            image = images[image_number]
        else:
            image = secrets.choice(images)
            while image == last_image_for_command.get(event.command.name):
                image = secrets.choice(images)
            if len(images) > 1:
                last_image_for_command[event.command.name] = image
        await event.reply(image)

    async def coro_noselect(event):
        """Generic coroutine, without manual image selection."""
        await coro(event)

    for command_name, command_properties in reactions.items():
        aliases = command_properties.get("aliases", [])
        num_images = len(command_properties.get("images", []))
        if num_images > 1:
            new_command = commands.Command(coro, name=command_name, aliases=aliases)
            new_command.help = (
                f"Randomly posts any of {num_images} {command_name}-themed images.\n\n"
                "A number can be provided to select a specific image."
            )
        else:
            new_command = commands.Command(coro_noselect, name=command_name, aliases=aliases)
            new_command.help = f"Posts a {command_name}-themed image."
        processor.add_command(new_command)
