#!/usr/bin/env python3

"""Module loading and unloading commands."""

from sailor import commands


@commands.command(owner_only=True)
async def load(event, *, name):
    """Load a sailor module by name. Owner only.

    Example usage:
    load modules.core.ping
    """
    event.bot.config.setdefault("module_blacklist", [])
    if name in event.bot.config["module_blacklist"]:
        event.bot.config["module_blacklist"].remove(name)
        event.bot.save_config()
    event.bot.add_module(name, skip_duplicate_commands=True)
    await event.reply(f"Loaded module {name}")


@commands.command(owner_only=True)
async def reload(event, *, name):
    """Reload a sailor module by name. Owner only.

    Example usage:
    reload modules.core.ping
    """
    event.bot.remove_module(name)
    event.bot.add_module(name)
    await event.reply(f"Reloaded module {name}")


@reload.command(name="--all", aliases=["-a"], owner_only=True)
async def reloadall(event):
    """Reload all modules."""
    module_names = list(event.bot.modules.keys())
    errors = []
    for module_name in module_names:
        try:
            event.bot.remove_module(module_name)
            event.bot.add_module(module_name)
        except Exception as error:
            errors.append((f"Could not reload module {module_name}: "
                           f"{error}"))

    if errors:
        await event.reply("\n".join(errors))
    await event.reply(f"Reloaded all modules.")


@commands.command(owner_only=True)
async def unload(event, *, name):
    """Unload a sailor module by name. Owner only.

    Example usage:
    unload modules.core.ping
    """
    event.bot.config.setdefault("module_blacklist", [])
    if name not in event.bot.config["module_blacklist"]:
        event.bot.config["module_blacklist"].append(name)
        event.bot.save_config()
    event.bot.remove_module(name)
    await event.reply(f"Unloaded module {name}")
