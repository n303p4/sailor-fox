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
        "<title>List of sailor-fox commands by module</title>",
        '<style type="text/css">',
        "body { font-family: Liberation Sans, Arial, sans-serif; }",
        "details { padding: 4px 0; }",
        "details:nth-of-type(2n) { background: #EEE; }",
        "summary > h2 { display: inline; }",
        "details > h2:first-of-type { margin-top: 0.3em; }",
        "details > h2 { width: 100%; border-bottom: 1px solid gray; }",
        '</style>',
        "</head>",
        "<body>",
        "<h1>List of sailor-fox commands by module</h1>",
        "<p>Arguments enclosed in <code>[]</code> are optional.</p>"
    ]
    previous_module = None
    for command in sorted(processor.commands.values(), key=lambda c: c.coro.__module__):
        if previous_module != command.coro.__module__:
            if previous_module:
                html.append("</details>")
            html += [
                "<details open>",
                "<summary>",
                f"<h2>{command.coro.__module__}</h2>",
                "</summary>"
            ]
            previous_module = command.coro.__module__
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
        html.append(markdown.markdown("\n\n".join(command_info)))

    html += ["</details>", "</body>", "</html>"]

    print("\n".join(html))


if __name__ == "__main__":
    main()
