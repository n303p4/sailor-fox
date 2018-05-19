#!/usr/bin/env python3
# pylint: disable=C0103

"""Trivia module with a trivia command."""

import random

import async_timeout
from sailor import commands
from sailor.web_exceptions import WebAPIUnreachable

URL_NUMBERS_API = "http://numbersapi.com/{0}/{1}"
OPTIONS_NUMBERS_API = ["math", "trivia"]

systemrandom = random.SystemRandom()


def generate_query_url(number, kind):
    """Given a number and a type of query, generate a query URL for the numbers API."""
    url = URL_NUMBERS_API.format(number, kind)
    return url


async def query(session, url):
    """Given a ClientSession and url, query the numbers API and get a fact."""
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            if response.status == 200:
                response_content = await response.text()
                return response_content
            raise WebAPIUnreachable(service="numbersapi.com")


@commands.cooldown(12, 12)
@commands.command(aliases=["numberfact", "number"])
async def numfact(ctx, number: int):
    """Display a random fact about a number."""
    kind = systemrandom.choice(OPTIONS_NUMBERS_API)
    url = generate_query_url(number, kind)
    fact = await query(ctx.bot.session, url)
    await ctx.send(fact)
