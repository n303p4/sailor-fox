"""Extension that handles kitsu.io queries.

Ported from Oxylibrium's Nestbot.
"""

from sailor import commands
from sailor.web_exceptions import WebAPIInvalidResponse, WebAPIUnreachable

from sailor_fox.helpers import FancyMessage

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
    async with session.get(url, params=params, timeout=10) as response:
        if response.status != 200:
            raise WebAPIUnreachable(service="kitsu.io")
        try:
            resp_content = await response.json(content_type="application/vnd.api+json")
        except Exception as error:
            raise WebAPIInvalidResponse(service="kitsu.io") from error

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

    except Exception as error:
        raise WebAPIInvalidResponse(service="kitsu.io") from error


async def _kitsu(request_type, event, query):
    request_type = filter_request_type(request_type)
    url = generate_search_url(request_type)

    params = {
        "filter[text]": query,
        "page[limit]": 1
    }

    response_content = await search(event.processor.session, url, params)
    result = generate_parsed_result(response_content, request_type)

    message = FancyMessage(event.f)

    for name, value in result["fields"].items():
        message.add_field(name=name, value=value)
    message.add_line(result["url"])

    await event.reply(message)


@commands.cooldown(6, 12)
@commands.command(aliases=["kitsu"])
async def anime(event, *, query):
    """Query kitsu.io for anime."""
    await _kitsu("anime", event, query)


@commands.cooldown(6, 12)
@commands.command()
async def manga(event, *, query):
    """Query kitsu.io for manga."""
    await _kitsu("manga", event, query)
