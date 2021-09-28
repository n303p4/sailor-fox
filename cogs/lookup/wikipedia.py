"""This cog contains a Wikipedia query command."""

import urllib.parse

from sailor import commands
from sailor.web_exceptions import WebAPIInvalidResponse, WebAPINoResultsFound, WebAPIUnreachable

from sailor_fox.helpers import FancyMessage

BASE_URL_WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php?{0}"


def generate_search_url(query):
    """Given a query, generate a search URL for Wikipedia's API."""
    params = urllib.parse.urlencode({"action": "opensearch", "search": query})
    url = BASE_URL_WIKIPEDIA_API.format(params)
    return url


async def search(session, url):
    """Given a ClientSession and URL, query the URL and return its response content as a JSON."""
    async with session.get(url, timeout=10) as response:
        if response.status != 200:
            raise WebAPIUnreachable(service="Wikipedia")
        try:
            response_content = await response.json()
        except Exception as error:
            raise WebAPIInvalidResponse(service="Wikipedia") from error

    return response_content


def generate_parsed_results(response_content):
    """Given response content from Wikipedia, parse content into a more easily readable form."""
    try:
        if not response_content[1]:
            raise WebAPINoResultsFound(message="No results found.")

        results = []

        for index in range(0, min(3, len(response_content[1]))):
            result = {
                "title": response_content[1][index],
                "url": response_content[3][index]
            }
            results.append(result)

        return results

    except Exception as error:
        raise WebAPIInvalidResponse(service="Wikipedia") from error


@commands.cooldown(6, 12)
@commands.command(aliases=["wikipedia"])
async def wiki(event, *, query):
    """Search Wikipedia.

    * `query` - A string to be used in the search criteria.
    """
    url = generate_search_url(query)
    response_content = await search(event.processor.session, url)
    results = generate_parsed_results(response_content)

    message = FancyMessage(event.f, sep="\n\n")
    for result in results:
        message.add_field(name=result["title"], value=event.f.no_embed_link(result["url"]), sep="\n")

    await event.reply(message)
