#!/usr/bin/env python3

"""Expression evaluation commands."""

import subprocess

from sailor import commands, exceptions


@commands.command(name="sh", owner_only=True)
async def shell(ctx, *args):
    """Execute a system command. Bot owner only."""
    if not args:
        raise exceptions.UserInputError("No shell command given.")
    process = subprocess.Popen(
        args,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    try:
        output, _ = process.communicate(timeout=8)
        process.terminate()
        output = ctx.f.codeblock(output)
    except subprocess.TimeoutExpired:
        process.kill()
        output = "Command timed out. x.x"
    await ctx.send(output)

@commands.command(name="exec", owner_only=True)
async def _exec(ctx, *, code):
    """Execute arbitrary Python code. Bot owner only."""
    variables = {
        "ctx": ctx,
        "create_task": ctx.bot.loop.create_task,
    }
    exec(code, {}, variables)
    del variables["ctx"], variables["create_task"]
    output = "\n".join([
        f"{type(value).__name__} {key}: {value}" for key, value in variables.items()
    ])
    if output:
        await ctx.send(ctx.f.codeblock(output))
    else:
        await ctx.send("No variables in execution.")
