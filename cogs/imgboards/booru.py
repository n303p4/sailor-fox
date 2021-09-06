"""Imageboard lookup commands."""

# pylint: disable=C0103

import json
import urllib.parse
import secrets

from bs4 import BeautifulSoup

from sailor import commands
from sailor.web_exceptions import WebAPIInvalidResponse, WebAPINoResultsFound, WebAPIUnreachable

BASE_URLS = {"safebooru": {"image_search": "https://safebooru.org/index.php?{0}",
                           "tag_search": "https://safebooru.org/autocomplete.php?{0}",
                           "image_post": "https://safebooru.org/index.php?page=post&s=view&id={0}"}}
MAX_LENGTH_TAGS = 200
TAGS_BLACKLIST = ["loli", "shota", "lolicon", "shotacon", "scat"]


async def _booru_tag_search(session, base_url: str, search_text: str = "", blacklist: list = None):
    """Generic helper that can find tags on booru-type sites."""
    if not blacklist:
        blacklist = TAGS_BLACKLIST
    query_params = urllib.parse.urlencode({"q": search_text.replace(" ", "_")})
    url = base_url.format(query_params)
    async with session.get(url) as response:
        if response.status == 200:
            try:
                results = json.loads(await response.text())
            except Exception as error:
                raise WebAPIInvalidResponse(service="Safebooru") from error
            if not results:
                raise WebAPINoResultsFound(message="No tags found.")
            return [result["label"] for result in results if result["value"] not in blacklist]
    raise WebAPIUnreachable(service="Safebooru")


async def _booru(session, base_url_api: str, tags: list = None, blacklist: list = None):
    """Generic helper command that can retrieve image posts from most 'booru-type sites."""
    if not tags:
        tags = []
    tags = [tag.replace(" ", "_") for tag in tags]
    if not blacklist:
        blacklist = TAGS_BLACKLIST
    for tag in blacklist:
        tags.append(f"-{tag}")
    query_params = urllib.parse.urlencode({
        "page": "dapi",
        "s": "post",
        "q": "index",
        "tags": " ".join(tags)
    })
    url = base_url_api.format(query_params)
    async with session.get(url) as response:
        if response.status == 200:
            try:
                xml = await response.text()
                soup = BeautifulSoup(xml, features="lxml")
                posts = soup.find_all("post")
                if not posts:
                    raise WebAPINoResultsFound(message=(
                        "No results found. Make sure you're using standard booru-type tags, such as "
                        "fox_ears or red_hair. You can use the command `sbt` to find valid tags."
                    ))
                post = secrets.choice(posts)
                return post
            except Exception as error:
                raise WebAPIInvalidResponse(service="Safebooru") from error
    raise WebAPIUnreachable(service="Safebooru")


def _process_post(post, formatter, base_url_post: str, max_length_tags: int=MAX_LENGTH_TAGS):
    """Make an embed that renders a 'booru post."""
    post_url = base_url_post.format(post["id"])
    lines = [
        formatter.bold("Original post: ") + formatter.no_embed_link(post_url),
        formatter.bold("Image URL: ") + post['file_url'],
        formatter.bold("Tags: ") + formatter.monospace(post["tags"][:max_length_tags].strip())
    ]
    return "\n".join(lines)


@commands.cooldown(6, 12)
@commands.command(aliases=["sbt"])
async def safeboorutag(event, *, search_text):
    """Search Safebooru for valid tags.

    * search_text - Text to search for.
    """
    result = await _booru_tag_search(event.processor.session, BASE_URLS["safebooru"]["tag_search"], search_text)
    formatted_results = "\n".join([r.replace("_", "\\_") for r in result])
    message = [event.f.bold("Matching tags"), formatted_results]
    await event.reply("\n".join(message))


@commands.cooldown(6, 12)
@commands.command(aliases=["sbooru", "sb"])
async def safebooru(event, *tags):
    """Fetch a random image from Safebooru. Tags accepted.

    * tags - A list of tags to be used in the search criteria.

    **Usage notes**
    * Valid tags can be found using the `sbt` command.
    * Underscores do not have to be used. But multi-word tags should be surrounded with quotes, e.g. \"fox ears\".

    See http://safebooru.org/index.php?page=help&topic=cheatsheet for more details.
    """
    result = await _booru(event.processor.session, BASE_URLS["safebooru"]["image_search"], tags)
    message = _process_post(result, event.f, BASE_URLS["safebooru"]["image_post"])
    await event.reply(message)


@commands.cooldown(6, 12)
@commands.command(aliases=["meido"])
async def maid(event, *tags):
    """Find a random maid. Optional tags."""
    result = await _booru(event.processor.session, BASE_URLS["safebooru"]["image_search"], ["maid"] + list(tags))
    message = _process_post(result, event.f, BASE_URLS["safebooru"]["image_post"])
    await event.reply(message)


@commands.cooldown(6, 12)
@commands.command(aliases=["animememe"])
async def animeme(event, *tags):
    """Find a random anime meme. Optional tags."""
    result = await _booru(event.processor.session, BASE_URLS["safebooru"]["image_search"], ["meme"] + list(tags))
    lines = _process_post(result, event.f, BASE_URLS["safebooru"]["image_post"])
    await event.reply(lines)


@commands.cooldown(6, 12)
@commands.command(name=":<")
async def colonlessthan(event, *tags):
    """:<"""
    result = await _booru(event.processor.session, BASE_URLS["safebooru"]["image_search"], [":<"] + list(tags))
    message = _process_post(result, event.f, BASE_URLS["safebooru"]["image_post"])
    await event.reply(message)
