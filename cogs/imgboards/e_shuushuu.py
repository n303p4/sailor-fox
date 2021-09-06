"""e-shuushuu module."""

import secrets
from urllib.parse import urlencode, urljoin

from bs4 import BeautifulSoup

from sailor import commands


BASE_URLS = {"e-shuushuu": {"image_search": "https://e-shuushuu.net/search/process/",
                            "tag_search": "https://e-shuushuu.net/httpreq.php?{0}",
                            "image_post": "https://e-shuushuu.net"}}
SEARCH_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


async def _eshuushuu_tag_search(session, base_url: str, search_text: str):
    query_params = urlencode({
        "mode": "tag_search",
        "tags": search_text.strip("\"'"),
        "type": 1
    })
    url = base_url.format(query_params)
    async with session.post(url) as response:
        if response.status < 400:
            return await response.text()
        else:
            raise Exception("Bad response from e-shuushuu")


async def _eshuushuu(session, base_url: str, search_headers: dict,
                     tags: list = None, characters: list = None):
    """Generic helper command that can handle e-shuushuu

    * site - The site to check.
    * tags - A list of tags to be used in the search criteria.
    """
    if not tags:
        tags = []
    tags = [f'"{tag}"' for tag in tags]

    if not characters:
        characters = []
    characters = [f'"{character}"' for character in characters]

    if not tags and not characters:
        raise Exception("You must provide at least one tag.")

    formdata = urlencode({
        "tags": "+".join(tags),
        "char": "+".join(characters)
    })
    async with session.post(base_url, data=formdata, headers=search_headers) as response:
        if response.status < 400:
            xml = await response.text()
            soup = BeautifulSoup(xml, features="lxml")
            posts = soup.find_all("a", href=True, class_="thumb_image")
            if not posts:
                raise Exception("No tags found.")
            post = secrets.choice(posts)["href"]
            return post
        else:
            raise Exception("Bad response from e-shuushuu")


@commands.cooldown(6, 12)
@commands.command(aliases=["est"])
async def eshuushuutag(event, *, search_text):
    """Search e-shuushuu for valid tags.

    This command does **not** currently accept character names.
    """
    result = await _eshuushuu_tag_search(
        event.processor.session,
        BASE_URLS["e-shuushuu"]["tag_search"],
        search_text
    )
    if result.strip("\n"):
        await event.reply(result)
    else:
        await event.reply("No matching tags were found.")


@commands.cooldown(6, 12)
@commands.command(aliases=["senko-san"])
async def senko(event, *tags):
    """Fetch a random Senko. Optional tags accepted."""
    result = await _eshuushuu(
        event.processor.session,
        BASE_URLS["e-shuushuu"]["image_search"],
        SEARCH_HEADERS,
        tags,
        ["Senko"]
    )
    image_url = urljoin(BASE_URLS["e-shuushuu"]["image_post"], result.lstrip("/"))
    await event.reply(image_url)


@commands.cooldown(6, 12)
@commands.command(aliases=["es", "shuushuu"])
async def eshuushuu(event, *tags):
    """Fetch a random image from e-shuushuu. You must provide at least one tag.

    * tags - A list of tags to be used in the search criteria.

    **Usage notes**
    * Valid tags can be found using the `est` command.
    * This command does **not** currently accept character names.
    * Multi-word tags should be surrounded with quotes, e.g. \"kitsune mimi\".
    """
    result = await _eshuushuu(
        event.processor.session,
        BASE_URLS["e-shuushuu"]["image_search"],
        SEARCH_HEADERS,
        tags
    )
    image_url = urljoin(BASE_URLS["e-shuushuu"]["image_post"], result.lstrip("/"))
    await event.reply(image_url)
