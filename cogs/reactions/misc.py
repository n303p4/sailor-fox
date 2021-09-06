"""Lookup commands that query various image APIs."""

# pylint: disable=C0103

import json
import secrets

import async_timeout

from sailor import commands
from sailor.web_exceptions import WebAPIUnreachable, WebAPIInvalidResponse

URL_RANDOM_DOG_API = "https://random.dog/woof.json"
URL_RANDOM_CAT_API = "https://nekos.life/api/v2/img/meow"
URL_RANDOM_NEKO_API = "https://nekos.life/api/neko"
URL_BIRBS_SUBREDDIT_TOP_API = "https://www.reddit.com/r/Birbs/top/.json"
URL_BIRBS_SUBREDDIT_NEW_API = "https://www.reddit.com/r/Birbs/top/.json"
URL_FOX_SUBREDDIT_TOP_API = "https://www.reddit.com/r/foxes/top/.json"
URL_FOX_SUBREDDIT_NEW_API = "https://www.reddit.com/r/foxes/new/.json"
URL_WOLF_SUBREDDIT_TOP_API = "https://www.reddit.com/r/wolves/top/.json"
URL_WOLF_SUBREDDIT_NEW_API = "https://www.reddit.com/r/wolves/new/.json"
URL_BEAVER_SUBREDDIT_TOP_API = "https://www.reddit.com/r/Beavers/top/.json"
URL_BEAVER_SUBREDDIT_NEW_API = "https://www.reddit.com/r/Beavers/new/.json"
URL_RACCOON_SUBREDDIT_TOP_API = "https://www.reddit.com/r/Raccoons/top/.json"
URL_RACCOON_SUBREDDIT_NEW_API = "https://www.reddit.com/r/Raccoons/new/.json"


async def query(session, url, service_name):
    """Given a ClientSession, URL, and service name, query an API."""
    try:
        async with async_timeout.timeout(10):
            async with session.get(url) as response:
                if response.status == 200:
                    response_content = await response.text()
                    return response_content
                else:
                    raise WebAPIInvalidResponse(service=service_name)
    except Exception as error:
        raise WebAPIUnreachable(service=service_name) from error


async def get_reddit_image(event, *urls):
    """Get a random image from a list of subreddits."""
    base_url = secrets.choice(urls)
    response_content = await query(event.processor.session, base_url, "Reddit")
    response_content = json.loads(response_content)
    children = response_content["data"]["children"]
    child = secrets.choice(children)
    url = child["data"]["url"]
    await event.reply(url)


@commands.cooldown(6, 12)
@commands.command(aliases=["doge"])
async def dog(event):
    """Fetch a random dog."""
    response_content = await query(event.processor.session, URL_RANDOM_DOG_API, "random.dog")
    response_content = json.loads(response_content)
    url = response_content["url"]
    await event.reply(url)


@commands.cooldown(6, 12)
@commands.command(aliases=["feline"])
async def cat(event):
    """Fetch a random cat."""
    response_content = await query(event.processor.session, URL_RANDOM_CAT_API, "nekos.life")
    response_content = json.loads(response_content)
    url = response_content["url"]
    await event.reply(url)


@commands.cooldown(6, 12)
@commands.command(aliases=["kemonomimi", "kmimi"])
async def kemono(event):
    """Fetch a random animal-eared person."""
    response_content = await query(event.processor.session, URL_RANDOM_NEKO_API, "nekos.life")
    response_content = json.loads(response_content)
    url = response_content["neko"]
    await event.reply(url)


@commands.cooldown(6, 12)
@commands.command()
async def birb(event):
    """Fetch a random birb."""
    await get_reddit_image(event, URL_BIRBS_SUBREDDIT_TOP_API, URL_BIRBS_SUBREDDIT_NEW_API)


@commands.cooldown(6, 12)
@commands.command()
async def fox(event):
    """Fetch a random fox."""
    await get_reddit_image(event, URL_FOX_SUBREDDIT_TOP_API, URL_FOX_SUBREDDIT_NEW_API)


@commands.cooldown(6, 12)
@commands.command()
async def wolf(event):
    """Fetch a random wolf."""
    await get_reddit_image(event, URL_WOLF_SUBREDDIT_TOP_API, URL_WOLF_SUBREDDIT_NEW_API)


@commands.cooldown(6, 12)
@commands.command()
async def beaver(event):
    """Fetch a random beaver."""
    await get_reddit_image(event, URL_BEAVER_SUBREDDIT_TOP_API, URL_BEAVER_SUBREDDIT_NEW_API)


@commands.cooldown(6, 12)
@commands.command()
async def raccoon(event):
    """Fetch a random raccoon."""
    await get_reddit_image(event, URL_RACCOON_SUBREDDIT_TOP_API, URL_RACCOON_SUBREDDIT_NEW_API)
