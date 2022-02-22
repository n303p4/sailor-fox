# How to run sailor-fox

This guide walks you through how to prepare your PC or server to run sailor-fox.
It assumes that you have working knowledge of a terminal/command line,
as well as working knowledge of JSON.

> ### Note
> The commands in this guide may need to be adjusted depending on your operating system
> and the location of your Python installation.

## Quickstart on Linux

```bash
wget https://gitlab.com/n303p4/sailor-fox/-/archive/master/sailor-fox-master.zip

unzip sailor-fox-master

cd sailor-fox-master

python3 -m pip install --user -r requirements.txt

cp config.example.json config.json

# Required for Discord and Twitch
nano config.json

# Required for Discord only
npm install axios discord.js
python3 deploy_discord_commands.py

python3 server.py
```

Separate terminal:

```bash
cd sailor-fox-master

# Command line
python3 cli_client.py

# Discord
node discord-client.js

# Twitch
python3 twitch_client.py
```

## Getting sailor-fox

[Download](https://gitlab.com/n303p4/sailor-fox/-/archive/master/sailor-fox-master.zip) and
extract sailor-fox to a folder. Afterwards, open a terminal or command prompt, and set
your working directory to the folder you extracted to:

```bash
cd sailor-fox
```

Keep the terminal/command prompt open, as you will need to use it for future commands.

## Installing dependencies

sailor-fox requires Python 3.7 or higher.
If you run Windows or macOS, you should download and install Python from the
[official website](http://python.org/).
If you run Linux, you should probably install Python from your package manager.
Most Linux distributions currently ship Python 3.7 or higher (as of September 2021).

On Windows and macOS, consider
[adding Python to your `PATH` environment variable](https://www.geeksforgeeks.org/how-to-add-python-to-windows-path/).
Otherwise, you will have to enter the full path to the Python executable for many
subsequent commands.

After installing Python, install additional dependencies:

```bash
python3 -m pip install --user -r requirements.txt
```

> ### Note
> If the above Python command does not work, note that `pip` is provided by a separate package
on many Linux distros (e.g. `python3-pip` on Ubuntu).

### Discord

The Discord client additionally depends on Node.js 16 or higher.
Most distributions don't ship this version, so you may have to follow
[these instructions](https://github.com/nodesource/distributions/blob/master/README.md).

On Windows and macOS, Node.js should be downloaded and installed from the
[official website](https://nodejs.org/en/).

After installing Node, install additional dependencies:

```bash
npm install axios discord.js
```

## Configuration

The bot should include a sample configuration file called [config.example.json](config.example.json).
Rename or copy it to `config.json` and fill it out accordingly.
For most chat services, you will need a token to authenticate with the service.

The bot's **prefix** is set in `config.json`.
The bot will only respond to messages that start with the prefix.
You should ideally set it to something that's easy to type.
If the bot will share a chat with other bots, the prefix should be unique to avoid collisions.

> ### Note
> You can set the prefix to an empty string, which will make the bot respond to every message in chat.
However, this is discouraged.

> ### Note
> The Discord client uses `discord_slash_prefix` instead, and you will need to put a `/` in front
of it to activate the bot. For example, if `discord_slash_prefix` is `c`, then you will have to
type `/c` as your prefix.

## Disable unwanted commands

sailor-fox includes a number of modules ("cogs"), each of which contains one or more commands.
It is likely that some of these commands are **not** suitable for your
Discord server/Twitch chat/IRC channel/etc.
You should review them, and disable what you don't need or want.
Visit [docs/commands](docs/commands) for a full list of commands.

Disabled modules are listed in `config.json` under the array `module_blocklist`.
For example, if you want to disable [cogs/owner/exec.py](cogs/owner/exec.py), add
`"cogs.owner.exec"` to the array.
To enable a module, simply delete it from the array.
It is currently not possible to disable or enable individual commands in a module.

You can also enable and disable modules while the bot is running.
To disable a module from the bot itself, run the command `unload <module.name>`
(remember to start it with the prefix).
For example, if you want to disable [cogs/owner/exec.py](cogs/owner/exec.py), run
`unload cogs.owner.exec`.
To enable a module, run `load <module name>`.

## Discord setup

Skip this step if you don't plan to run sailor-fox as a Discord bot.

Visit the [Discord Developer Portal](https://discord.com/developers/applications)
to create an application.
When you create your application, click the "Bot" tab and click "Add Bot".
You will have to copy your bot token from here.

In `config.json`, fill out the fields that start with `discord_`. `discord_token`
should be the token from the bot page earlier.

To get the user ID for a Discord user (to fill out `discord_owner_ids`), refer to
[this support page](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-).
User IDs in `config.json` should be strings, not integers!

> ### Note
> If `discord_owner_ids` is left empty, then none of the owner-only
commands will work through Discord.

Once `config.json` is filled out, run the following command in a terminal:

```bash
python3 deploy_discord_commands.py
```

This will register a command on Discord's servers for interacting with the bot, named
after `discord_slash_prefix` in `config.json`. Command registration can take from a
few minutes to one hour, so hang tight!

Finally, to invite the bot to your server, use this link:

```bash
# replace APPLICATION_ID with the ID of your bot
https://discord.com/oauth2/authorize?client_id=APPLICATION_ID&scope=bot%20applications.commands
```

## Twitch setup

Skip this step if you don't plan to run sailor-fox as a Twitch bot.

In `config.json`, fill out the fields that start with `twitch_`.

Create a new Twitch account for the bot. `twitch_username` should be the
account name you created for the bot, not your own Twitch username!

To get a valid token for `twitch_token`, refer to the
[Twitch IRC bot documentation](https://dev.twitch.tv/docs/irc).

To get the user ID for a Twitch user (to fill out `twitch_owner_ids`), you can use
[this StreamWeasels tool](https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/).
User IDs in `config.json` should be strings, not integers!

> ### Note
> If `twitch_owner_ids` is left empty, then none of the owner-only
commands will work through Twitch chat.

## Running sailor-fox

In a terminal, run:

```bash
python3 server.py
```

The following commands should be run in a separate terminal:

### Change directories (if needed)

```bash
cd sailor-fox
```

### Command line

```bash
python3 cli_client.py
```

### Discord

```bash
node discord-client.js
```

### Discord classic (deprecated)

```bash
python3 discord_classic_client.py
```

### Twitch

```bash
python3 twitch_client.py
```

## Autostarting with systemd

For convenience, you may want your bot to autostart on a Linux server, even after reboots.
Some service templates are contained in the `systemd` folder.
Edit them as needed, and copy them to `/etc/systemd/system/`.

Then in a terminal, run:

```bash
sudo systemctl enable --now sailor-fox-server  # Server

sudo systemctl enable --now sailor-fox-discord  # Discord

sudo systemctl enable --now sailor-fox-discord-classic  # Discord (classic)

sudo systemctl enable --now sailor-fox-twitch  # Twitch
```
