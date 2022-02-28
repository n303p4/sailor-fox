"""Bot help command."""

import inspect

from sailor import commands
from sailor.exceptions import CommandNotFound

from sailor_fox.helpers import FancyMessage


@commands.cooldown(6, 12)
@commands.command(name="help", aliases=["commands"])
async def help_(event, *command_name):
    """Help command. Run `help (command name)` for more information on a specific command.

    **Example usage**

    * `help`
    * `help ping`
    * `help info`
    """
    if command_name:
        parent = event.processor
        for token in command_name:
            cmd = parent.all_commands.get(token)
            if not cmd:
                break
            parent = cmd
        if not cmd:
            raise CommandNotFound(name=" ".join(command_name))
        else:
            help_text = [f"# {cmd.name}"]
            if cmd.aliases:
                help_text.append(f"Aliases: {', '.join(cmd.aliases)}")
            arguments = []
            for parameter in list(cmd.signature.parameters.values())[1:]:
                if parameter.default == inspect.Parameter.empty:
                    arguments.append(parameter.name)
                else:
                    arguments.append(f"[{parameter.name}={parameter.default}]")
            if arguments:
                help_text.append(f"Arguments: {' '.join(arguments)}")
            help_text.append(f"\n{cmd.help}")
            if cmd.commands:
                help_text.append("\n# Child commands:")
                for child_cmd_name in cmd.commands.keys():
                    help_text.append(f"{cmd.name} {child_cmd_name}")
            await event.reply(event.f.codeblock("\n".join(help_text)))
    else:
        command_categories = {}

        for command in event.processor.commands.values():
            module_name = command.coro.__module__.split(".")
            if len(module_name) == 1:
                command_category = module_name[0]
            else:
                command_category = module_name[0] if module_name[0] != "cogs" else module_name[1]
            command_category = command_category.replace("_", " ").title()
            if command_category not in command_categories:
                command_categories[command_category] = []
            command_categories[command_category].append(command.name)
            if len(command.aliases) > 10:
                command_categories[command.name.capitalize()] = command.aliases

        message = FancyMessage(formatter=event.f, sep="\n")
        for command_category in sorted(command_categories.keys()):
            commands = command_categories[command_category]
            message.add_line(f"# {command_category}")
            message.add_line(", ".join(sorted(commands)))
            message.add_line()

        message.add_line("Run `help <command name>` for more details on a command.")

        await event.reply(event.f.codeblock(message))
