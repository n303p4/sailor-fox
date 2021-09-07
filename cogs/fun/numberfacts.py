"""Trivia module with a trivia command."""

# pylint: disable=invalid-name

import secrets

from sailor import commands
from sailor.web_exceptions import WebAPIUnreachable

URL_NUMBERS_API = "http://numbersapi.com/{0}/{1}"
OPTIONS_NUMBERS_API = ["math", "trivia"]


def generate_query_url(number, kind):
    """Given a number and a type of query, generate a query URL for the numbers API."""
    url = URL_NUMBERS_API.format(number, kind)
    return url


async def query(session, url):
    """Given a ClientSession and url, query the numbers API and get a fact."""
    async with session.get(url, timeout=10) as response:
        if response.status != 200:
            raise WebAPIUnreachable(service="numbersapi.com")
        response_content = await response.text()
        return response_content


@commands.cooldown(12, 12)
@commands.command(aliases=["numberfact", "number"])
async def numfact(event, number: int = None):
    """Display a random fact about a number."""
    if not isinstance(number, int):
        number = secrets.randbelow(101)
    kind = secrets.choice(OPTIONS_NUMBERS_API)
    url = generate_query_url(number, kind)
    fact = await query(event.processor.session, url)
    await event.reply(fact)
