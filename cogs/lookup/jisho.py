"""jisho.org query command."""

import urllib.parse

import async_timeout
from sailor import commands
from sailor.web_exceptions import WebAPIInvalidResponse, WebAPINoResultsFound, WebAPIUnreachable

BASE_URL_JISHO_API = "http://jisho.org/api/v1/search/words?{0}"


def embed(event, **fields):
    """Generate a fancy embed."""
    field_data = "\n".join(f"{event.f.bold(n)}: {i}" for n, i in fields.items())
    return field_data


def generate_search_url(query):
    """Given a query, generate a search URL for jisho.org's API."""
    params = urllib.parse.urlencode({"keyword": query})
    url = BASE_URL_JISHO_API.format(params)
    return url


async def search(session, url):
    """Given a ClientSession and URL, query the URL and return its response content as a JSON."""
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            if response.status == 200:
                try:
                    response_content = await response.json()
                except Exception as error:
                    raise WebAPIInvalidResponse(service="jisho.org") from error
            raise WebAPIUnreachable(service="jisho.org")

    return response_content


def generate_parsed_result(response_content):
    """Given response content from jisho.org, parse content into a more easily readable form."""
    try:
        if not response_content.get("data"):
            raise WebAPINoResultsFound(message="No result found.")

        japanese = response_content["data"][0]["japanese"][0]
        sense = response_content["data"][0]["senses"][0]
        english_string = ", ".join(sense["english_definitions"])

        result = {
            "kanji": str(japanese.get("word")),
            "kana": str(japanese.get("reading")),
            "english": english_string
        }

        return result

    except Exception as error:
        raise WebAPIInvalidResponse(service="jisho.org") from error


@commands.cooldown(6, 12)
@commands.command(aliases=["jp"])
async def jisho(event, *, query):
    """Translate a word into Japanese.

    Example usage:
    jisho test
    """
    url = generate_search_url(query)
    response_content = await search(event.processor.session, url)
    result = generate_parsed_result(response_content)

    fields = {
        "Kanji": result["kanji"],
        "Kana": result["kana"],
        "English": result["english"]
    }
    message = embed(**fields)

    await event.reply(message)
