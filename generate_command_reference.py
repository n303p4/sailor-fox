"""Generate command documentation."""

import inspect
import os
import sys

from sailor.commands import Processor


def main():
    """Factory to create and run everything."""

    dirpath_docs_commands = os.path.join(os.path.dirname(os.path.realpath(__file__)), "docs", "commands")

    if os.path.isfile(dirpath_docs_commands):
        os.remove(dirpath_docs_commands)
    if not os.path.isdir(dirpath_docs_commands):
        os.makedirs(dirpath_docs_commands)

    processor = Processor()

    processor.add_modules_from_dir("cogs", blocklist=["cogs.myriad.all"])

    commands_for_modules = {}

    for command in sorted(processor.commands.values(), key=lambda c: c.coro.__module__):
        if command.coro.__module__ not in commands_for_modules:
            commands_for_modules[command.coro.__module__] = [
                sys.modules[command.coro.__module__].__doc__.strip(),
                "Note: Arguments enclosed in `[]` are optional."
            ]
        command_info = [f"## `{command.name}`"]
        if command.aliases:
            command_info.append(f"**Aliases:** `{', '.join(command.aliases)}`")
        arguments = []
        for parameter in list(command.signature.parameters.values())[1:]:
            if parameter.default == inspect.Parameter.empty:
                arguments.append(parameter.name)
            else:
                arguments.append(f"[{parameter.name}={parameter.default}]")
        if arguments:
            command_info.append(f"**Arguments:** `{' '.join(arguments)}`")
        command_info.append(command.help)
        commands_for_modules[command.coro.__module__].append("\n\n".join(command_info))

    for module, commands in commands_for_modules.items():
        commands_markdown = "\n\n".join(commands)
        with open(os.path.join(dirpath_docs_commands, f"{module}.md"), "w") as file_object:
            file_object.write(f"# {module}\n\n{commands_markdown}")


if __name__ == "__main__":
    main()
