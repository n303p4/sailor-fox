"""Module loading and unloading commands."""

from sailor import commands


@commands.command(owner_only=True)
async def load(event, *, name):
    """Load a sailor module by name. Owner only.

    Example usage:
    load modules.core.ping
    """
    event.processor.config.setdefault("module_blocklist", [])
    if name in event.processor.config["module_blocklist"]:
        event.processor.config["module_blocklist"].remove(name)
        event.processor.save_config()
    event.processor.add_module(name, skip_duplicate_commands=True)
    await event.reply(f"Loaded module {name}")


@commands.command(owner_only=True)
async def reload(event, *, name):
    """Reload a sailor module by name. Owner only.

    Example usage:
    reload modules.core.ping
    """
    event.processor.remove_module(name)
    event.processor.add_module(name)
    await event.reply(f"Reloaded module {name}")


@reload.command(name="--all", aliases=["-a"], owner_only=True)
async def reloadall(event):
    """Reload all modules."""
    module_names = list(event.processor.modules.keys())
    errors = []
    for module_name in module_names:
        try:
            event.processor.remove_module(module_name)
            event.processor.add_module(module_name)
        except Exception as error:  # pylint: disable=broad-except
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
    event.processor.config.setdefault("module_blocklist", [])
    if name not in event.processor.config["module_blocklist"]:
        event.processor.config["module_blocklist"].append(name)
        event.processor.save_config()
    event.processor.remove_module(name)
    await event.reply(f"Unloaded module {name}")
