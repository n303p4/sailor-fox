# cogs.imgboards.booru

Imageboard lookup commands.

Note: Arguments enclosed in `[]` are optional.

## `animeme`

**Aliases:** `animememe`

**Arguments:** `tags`

Find a random anime meme. Optional tags.

## `:<`

**Arguments:** `tags`

:<

## `maid`

**Aliases:** `meido`

**Arguments:** `tags`

Find a random maid. Optional tags.

## `safebooru`

**Aliases:** `sbooru, sb`

**Arguments:** `tags`

Fetch a random image from Safebooru. Tags accepted.

* `tags` - A list of tags to be used in the search criteria.

**Usage notes**

* Valid tags can be found using the `sbt` command.
* Underscores do not have to be used. But multi-word tags should be surrounded with quotes, e.g. "fox ears".

See http://safebooru.org/index.php?page=help&topic=cheatsheet for more details.

## `safeboorutag`

**Aliases:** `sbt`

**Arguments:** `search_text`

Search Safebooru for valid tags.

* `search_text` - Text to search for.