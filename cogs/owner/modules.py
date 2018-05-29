#!/usr/bin/env python3

"""Module loading and unloading commands."""

from sailor import commands


@commands.command(owner_only=True)
async def load(ctx, *, name):
    """Load a sailor module by name. Owner only.

    Example usage:
    load modules.core.ping
    """
    ctx.bot.config.setdefault("module_blacklist", [])
    if name in ctx.bot.config["module_blacklist"]:
        ctx.bot.config["module_blacklist"].remove(name)
        ctx.bot.save_config()
    ctx.bot.add_module(name, skip_duplicate_commands=True)
    await ctx.send(f"Loaded module {name}")


@commands.command(owner_only=True)
async def reload(ctx, *, name):
    """Reload a sailor module by name. Owner only.

    Example usage:
    reload modules.core.ping
    """
    ctx.bot.remove_module(name)
    ctx.bot.add_module(name)
    await ctx.send(f"Reloaded module {name}")


@reload.command(name="--all", aliases=["-a"], owner_only=True)
async def reloadall(ctx):
    """Reload all modules."""
    module_names = list(ctx.bot.modules.keys())
    errors = []
    for module_name in module_names:
        try:
            ctx.bot.remove_module(module_name)
            ctx.bot.add_module(module_name)
        except Exception as error:
            errors.append((f"Could not reload module {module_name}: "
                           f"{error}"))

    if errors:
        await ctx.send("\n".join(errors))
    await ctx.send(f"Reloaded all modules.")


@commands.command(owner_only=True)
async def unload(ctx, *, name):
    """Unload a sailor module by name. Owner only.

    Example usage:
    unload modules.core.ping
    """
    ctx.bot.config.setdefault("module_blacklist", [])
    if name not in ctx.bot.config["module_blacklist"]:
        ctx.bot.config["module_blacklist"].append(name)
        ctx.bot.save_config()
    ctx.bot.remove_module(name)
    await ctx.send(f"Unloaded module {name}")
