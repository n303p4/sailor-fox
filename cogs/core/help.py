"""Bot help command."""

import inspect

from sailor import commands


@commands.cooldown(6, 12)
@commands.command(name="help", aliases=["commands"])
async def help_(event, *, command_name: str = None):
    """Help command. Run help <command name> for more information on a specific command.

    Example usage:
    help
    help ping
    help info
    """
    if command_name:
        cmd = event.processor.all_commands.get(command_name)
        if not cmd:
            await event.reply(f"{command_name} is not a valid command.")
        else:
            help_text = cmd.name
            if cmd.aliases:
                help_text += f" (aliases: {', '.join(cmd.aliases)})"
            command_parameters = []
            for parameter in list(cmd.signature.parameters.values())[1:]:
                if parameter.default == inspect.Parameter.empty:
                    command_parameters.append(f"*{parameter.name}")
                else:
                    command_parameters.append(parameter.name)
            help_text += f"\nArguments: {', '.join(command_parameters)}"
            help_text += f"\n\n{cmd.help}"
            await event.reply(event.f.codeblock(help_text))
    else:
        commands_list = []

        for command in event.processor.commands.values():
            commands_list.append(command.name)
            if len(command.aliases) >= 10:
                commands_list += command.aliases

        help_text = event.f.codeblock(", ".join(sorted(commands_list)) + "\n")
        help_text = event.f.bold("List of commands:\n") + help_text
        help_text += f"\nRun {event.f.bold('help command')} for more details on a command."
        await event.reply(help_text)
