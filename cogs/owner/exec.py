"""Expression evaluation commands."""

# pylint: disable=exec-used

import subprocess

from sailor import commands, exceptions


@commands.command(name="sh", owner_only=True)
async def shell(event, *args):
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
        output = event.f.codeblock(output)
    except subprocess.TimeoutExpired:
        process.kill()
        output = "Command timed out. x.x"
    await event.reply(output)


@commands.command(name="exec", owner_only=True)
async def _exec(event, *, code):
    """Execute arbitrary Python code. Bot owner only."""
    variables = {
        "event": event,
        "create_task": event.processor.loop.create_task,
    }
    exec(code, {}, variables)
    del variables["event"], variables["create_task"]
    output = "\n".join([
        f"{type(value).__name__} {key}: {value}" for key, value in variables.items()
    ])
    if output:
        await event.reply(event.f.codeblock(output))
    else:
        await event.reply("No variables in execution.")
