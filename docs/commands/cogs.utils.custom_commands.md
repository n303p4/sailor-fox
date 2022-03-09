# cogs.utils.custom_commands

Manage and activate custom commands.

These can be potentially dangerous! Be careful out there.

Note: Arguments enclosed in `[]` are optional.

## `custom`

**Aliases:** `cc, c`

**Arguments:** `[name=None] args`

Execute a custom command.

**Example usage**

* `custom ping`
* `custom hello world`
* `custom multiargtest a b c d`
* `custom ddg "bat eared fox"`
* `custom xkcd`
* `custom xkcd 2000`
* `custom xkcdprev`
* `custom bb0`
* `custom bbr`

## `custom list`

**Aliases:** `ls, l`

List all registered custom commands.

## `custom add`

**Aliases:** `a`

**Arguments:** `name tokens`

Add a custom command. Owner only.

**Example usage**

* `custom add ping Pong! :3`
* `custom add hello Hello, {0}!`
* `custom add multiargtest {0} {1} {2} {3}`
* `custom add ddg DuckDuckGo search result for {0}: html|a.result-link|https://lite.duckduckgo.com/lite?q={0}`
* `custom add xkcd html|#ctitle|https://xkcd.com/{0} | "html|#comic img|https://xkcd.com/{0}"`
* `custom add xkcdprev The second-most recent xkcd comic is html|a[rel=prev]|https://xkcd.com`
* `custom add bb0 From r/battlebots: json|data.children.0.data.url|https://old.reddit.com/r/battlebots/.json`
* `custom add bbr From r/battlebots: json|data.children.random.data.url|https://old.reddit.com/r/battlebots/.json`

## `custom add discordwebhook`

**Aliases:** `dw`

**Arguments:** `name discord_webhook_url tokens`

Add a custom command that POSTs to a Discord webhook. Owner only.

## `custom delete`

**Aliases:** `del, d, remove, rm, r`

**Arguments:** `name`

Delete a custom command by name. Owner only.

**Example usage**

* `custom delete bb`