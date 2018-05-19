#!/usr/bin/env python3

"""Extension that handles kitsu.io queries.

Ported from Oxylibrium's Nestbot.
"""

import async_timeout
import discord
from sailor import commands, exceptions
from sailor.web_exceptions import WebAPIInvalidResponse, WebAPIUnreachable

BASE_URL_KITSUIO = "https://kitsu.io/api/edge/{0}"
REQUEST_TYPES = [
    "anime",
    "manga"
]
FIELDS = {
    "Score": "averageRating",
    "Status": "status",
    "Started": "startDate"
}


def filter_request_type(request_type):
    """Given an arbitrary string, generate a valid request type for kitsu.io."""
    if request_type not in REQUEST_TYPES:
        request_type = REQUEST_TYPES[0]
    return request_type


def generate_search_url(request_type):
    """Given a request type, generate a query URL for kitsu.io."""
    url = BASE_URL_KITSUIO.format(request_type)
    return url


async def search(session, url, params):
    """Given a ClientSession and URL, query the URL and return its response content as a JSON."""
    async with async_timeout.timeout(10):
        async with session.get(url, params=params) as response:
            if response.status == 200:
                try:
                    resp_content = await response.json(content_type="application/vnd.api+json")
                except Exception:
                    raise WebAPIInvalidResponse(service="kitsu.io")
            else:
                raise WebAPIUnreachable(service="kitsu.io")

    return resp_content


def generate_parsed_result(response_content, request_type):
    """Parse response content from kitsu.io and return a dict."""
    try:
        attributes = response_content["data"][0]["attributes"]

        result = {
            "title_english": f"{attributes['titles'].get('en', '???')}",
            "title_romaji": f"{attributes['titles'].get('en_jp', '???')}",
            "url": f"https://kitsu.io/{request_type}/{attributes['slug']}",
            "description": attributes.get("synopsis", "None"),
            "fields": {}
        }

        for name, item in FIELDS.items():
            result["fields"][name] = attributes.get(item, "N/A")

        if attributes.get("endDate"):
            result["fields"]["Finished"] = attributes["endDate"]

        result["thumbnail"] = attributes.get("posterImage", {}).get("original")

        return result

    except Exception:
        raise WebAPIInvalidResponse(service="kitsu.io")


async def _kitsu(request_type, ctx, query):
    request_type = filter_request_type(request_type)
    url = generate_search_url(request_type)

    params = {
        "filter[text]": query,
        "page[limit]": 1
    }

    response_content = await search(ctx.bot.session, url, params)
    result = generate_parsed_result(response_content, request_type)

    url = result["url"]
    field_data = "\n".join(f"{ctx.f.bold(n)}: {i}" for n, i in result["fields"].items())

    message = "\n".join([field_data, url])

    await ctx.send(message)


@commands.cooldown(6, 12)
@commands.command(aliases=["kitsu"])
async def anime(ctx, *, query):
    """Query kitsu.io for anime."""
    await _kitsu("anime", ctx, query)


@commands.cooldown(6, 12)
@commands.command()
async def manga(ctx, *, query):
    """Query kitsu.io for manga."""
    await _kitsu("manga", ctx, query)
