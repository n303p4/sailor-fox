#!/usr/bin/env python3

"""Bot help command."""

from sailor import commands


@commands.cooldown(6, 12)
@commands.command(name="help", aliases=["commands"])
async def help_(ctx, command_name: str = None):
    """Help command. Run help <command name> for more information on a specific command.

    Example usage:
    help
    help ping
    help info
    """
    if command_name:
        cmd = ctx.bot.all_commands.get(command_name)
        if not cmd:
            await ctx.send(f"{command_name} is not a valid command.")
        else:
            await ctx.send(ctx.f.codeblock(f"{cmd.help}"))
    else:
        commands_list = []

        for command in ctx.bot.commands.values():
            commands_list.append(command.name)
            if len(command.aliases) >= 10:
                commands_list += command.aliases

        help_text = ctx.f.codeblock(", ".join(sorted(commands_list)) + "\n")
        help_text = ctx.f.bold("List of commands:\n") + help_text
        help_text += f"\nRun {ctx.f.bold('help command')} for more details on a command."
        await ctx.send(help_text)
