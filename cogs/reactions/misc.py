"""Lookup commands that query various image APIs."""

# pylint: disable=invalid-name

import json
import random

import async_timeout
from sailor import commands
from sailor.web_exceptions import WebAPIUnreachable

URL_RANDOM_DOG_API = "https://random.dog/woof.json"
URL_RANDOM_CAT_API = "https://nekos.life/api/v2/img/meow"
URL_RANDOM_BIRB = "https://random.birb.pw/img/{0}"
URL_RANDOM_BIRB_API = "https://random.birb.pw/tweet.json/"
URL_RANDOM_NEKO_API = "https://nekos.life/api/neko"
URL_FOX_SUBREDDIT_TOP_API = "https://www.reddit.com/r/foxes/top/.json"
URL_FOX_SUBREDDIT_NEW_API = "https://www.reddit.com/r/foxes/new/.json"

systemrandom = random.SystemRandom()

async def query(session, url, service_name):
    """Given a ClientSession, URL, and service name, query an API."""
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            if response.status == 200:
                response_content = await response.text()
                return response_content
            else:
                raise WebAPIUnreachable(service=service_name)


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
@commands.command(aliases=["catgirl", "kneko", "nekomimi",
                           "foxgirl", "kitsune", "kitsunemimi"])
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
    response_content = await query(event.processor.session, URL_RANDOM_BIRB_API, "random.birb.pw")
    response_content = json.loads(response_content)
    url = URL_RANDOM_BIRB.format(response_content["file"])
    await event.reply(url)


@commands.cooldown(6, 12)
@commands.command()
async def fox(event):
    """Fetch a random cat."""
    base_url = systemrandom.choice((URL_FOX_SUBREDDIT_TOP_API, URL_FOX_SUBREDDIT_NEW_API))
    response_content = await query(event.processor.session, base_url, "Reddit")
    response_content = json.loads(response_content)
    children = response_content["data"]["children"]
    foxxo = systemrandom.choice(children)
    url = foxxo["data"]["url"]
    await event.reply(url)
