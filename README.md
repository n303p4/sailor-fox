# sailor-fox

[![MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://gitlab.com/n303p4/kitsuchan-2/blob/master/LICENSE.txt)
[![Python](https://img.shields.io/badge/Python-3.6-brightgreen.svg)](https://python.org/)

**kitsuchan-bot** was a small, modular, command-oriented Discord bot written in `discord.py`,
with a focus on readable, portable, and easy to maintain code.

**sailor-fox** is a port of most of kitsuchan-bot
to the [sailor command framework](https://gitlab.com/n303p4/sailor), with some various bots
provided as examples.
In particular, it provides Discord and Twitch bots that may be of actual use.

# Before you begin

sailor-fox has a number of modules (cogs) that are likely **not** suitable for your server.
You should review them and disable what you don't need or want.

To disable a module from the bot itself, run the command `unload <module name>`.
For example, if you want to disable `exec.py` in `cogs/owner`, run `unload cogs.owner.exec`.
To enable a module, use `load <module name>`.

You can also manually edit the configuration if you prefer.
Disabled modules are in `config.json` under `module_blocklist` (see next section for details).

# How to run sailor-fox

sailor-fox requires Python 3.7 or higher.
If you're on Windows or macOS, you should download and install Python from the
[official Python website](http://python.org/).
If you're on Linux, you should probably install Python from your package manager.
Most Linux distributions currently ship Python 3.7 or higher (as of September 2021).

The Twitch bot also depends on Node.js >= 16.0.0.

The bot should include a sample configuration file called `config.example.json`.
Rename or copy it to `config.json` and fill it out accordingly.
For most chat services, you will also need a token to authenticate with the service.

Install necessary dependencies:

```bash
python3 -m pip install --user -r requirements.txt
npm install axios tmi.js  # For Twitch only
```

## Discord

Visit the [Discord Developer Portal](https://discord.com/developers/applications)
to create an application.
When you create your application, click the "Bot" tab and click "Add Bot".

In `config.json`, fill out the fields that start with `discord_`.

Then in a terminal, run:

```bash
python3 http_service.py
```

In a separate terminal, run:

```bash
python3 discord_bot.py
```

You may have to change the above commands slightly, depending on your operating system and the
location of your Python installation.

## Twitch

Refer to the [Twitch bot documentation](https://dev.twitch.tv/docs/irc).

In `config.json`, fill out the fields that start with `twitch_`.

Then in a terminal, run:

```bash
python3 http_service.py
```

In a separate terminal, run:

```bash
node twitch-bot.js
```

# Autostarting the bot

## systemd

TBD

# More technical stuff

## Architecture

sailor-fox is primarily designed around the **backend** service `http_service.py`.
This provides a JSON API over a local HTTP server (__not__ intended to be run over the web).
The backend contains an instance of `sailor.commands.Processor` that can interpret commands.
Commands are sent to the backend by HTTP POSTing a JSON object to `localhost`, default port `9980`.
The JSON object should follow this structure:

```json
{
    "id": <optional request id, for logging convenience>,
    "message": <message contents>,
    "is_owner": <optional check for whether the person who sent the command is the bot owner>,
    "character_limit": <character limit of the chat service>,
    "format_name": <optional format name>
}
```

The backend responds with a flat JSON array that contains zero or more strings.
If the HTTP status code is 200, the command completed normally.
Any other status code should be understood as an error.

To create a complete and useful bot, there must also be a **frontend** to a chat service.
Its job is to decide what messages in chat look like commands, and forward them to the backend.
Results are then returned back to the frontend for further processing.

While the backend is written in Python, frontends can be written in any language.
Multiple unrelated frontends can also share the same backend instance, allowing a common backend
to serve more than one chat service (i.e. less system resources required).

Taking this all together, the basic flow is as follows:

1. A message is posted in some chat service.
2. The frontend for that chat service reads the message.
    * If the message does not resemble a command (usually decided by a command prefix), stop here.
    * Otherwise, proceed to 3.
3. The frontend does some checks, such as whether the user who sent the message is the bot owner.
   It also cleans the message for forwarding to the backend (e.g. removing the prefix)
4. The frontend sends an HTTP POST request to the backend containing the aforementioned JSON object.
5. The backend receives and processes the request, then sends back a response containing
   a JSON array of messages.
6. The frontend receives the response and sends the message(s) in chat.

# Q&A

## Can I use sailor-fox for my project?

Sure! Just read over [`LICENSE.txt`](LICENSE.txt) for details - it's very short, I promise! I
don't like long licenses, and you probably don't, either.

## Can I request a feature?

I don't take requests, but I do try and listen to feedback! Feel free to submit any suggestions
you have under the issue tracker. I'll be sure to ask you questions if I have any, and if I reject
your ideas, I'll try to explain my reasons as best as I can.
