"""Generate command documentation."""

# pylint: disable=invalid-name

import inspect

import markdown

from sailor.commands import Processor


def main():
    """Factory to create and run everything."""

    processor = Processor()

    processor.add_modules_from_dir("cogs", blocklist=["cogs.myriad.all"])

    html = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<title>List of sailor-fox commands</title>",
        '<style type="text/css">',
        R"body { font-family: Liberation Sans, Arial, sans-serif; }",
        R"h1 { width: 100%; border-bottom: 1px solid gray; }",
        '</style>',
        "</head>",
        "<body>",
        "<h1>List of sailor-fox commands</h1>",
        "<p>Arguments enclosed in [] are optional.</p>"
    ]
    for command in sorted(processor.commands.values(), key=lambda x: x.name):
        command_info = [f"# `{command.name}`"]
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
        html.append(markdown.markdown("\n\n".join(command_info)))

    html += ["</body>", "</html>"]

    print("\n".join(html))


if __name__ == "__main__":
    main()
