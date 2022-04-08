"""Lookup commands that query various image APIs."""

# pylint: disable=C0103

import json
import secrets

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
URL_RACCOON_CLUB_RANDOM_API = "https://raccoon.club/api/random"
URL_RACCOON_SUBREDDIT_TOP_API = "https://www.reddit.com/r/Raccoons/top/.json"
URL_RACCOON_SUBREDDIT_NEW_API = "https://www.reddit.com/r/Raccoons/new/.json"


async def query(session, url, service_name):
    """Given a ClientSession, URL, and service name, query an API."""
    async with session.get(url, timeout=10) as response:
        if response.status != 200:
            raise WebAPIUnreachable(service=service_name)
        response_content = await response.text()
        return response_content


async def get_reddit_image(event, *urls):
    """Get a random image from a list of subreddits."""
    base_url = secrets.choice(urls)
    response_content = await query(event.processor.session, base_url, "Reddit")
    try:
        response_content = json.loads(response_content)
        children = response_content["data"]["children"]
        child = secrets.choice(children)
        url = child["data"]["url"]
        await event.reply(url)
    except Exception as error:
        raise WebAPIInvalidResponse(service="Reddit") from error


@commands.cooldown(6, 12)
@commands.command(aliases=["doge"])
async def dog(event):
    """Fetch a random dog.

    Image source: random.dog
    """
    try:
        response_content = await query(event.processor.session, URL_RANDOM_DOG_API, "random.dog")
        response_content = json.loads(response_content)
        url = response_content["url"]
    except Exception as error:
        raise WebAPIInvalidResponse(service="random.dog") from error
    await event.reply(url)


@commands.cooldown(6, 12)
@commands.command(aliases=["feline"])
async def cat(event):
    """Fetch a random cat.

    Image source: nekos.life
    """
    response_content = await query(event.processor.session, URL_RANDOM_CAT_API, "nekos.life")
    try:
        response_content = json.loads(response_content)
        url = response_content["url"]
    except Exception as error:
        raise WebAPIInvalidResponse(service="nekos.life") from error
    await event.reply(url)


@commands.cooldown(6, 12)
@commands.command(aliases=["kemonomimi", "kmimi"])
async def kemono(event):
    """Fetch a random animal-eared person.

    Image source: nekos.life
    """
    response_content = await query(event.processor.session, URL_RANDOM_NEKO_API, "nekos.life")
    try:
        response_content = json.loads(response_content)
        url = response_content["neko"]
    except Exception as error:
        raise WebAPIInvalidResponse(service="nekos.life") from error
    await event.reply(url)


@commands.cooldown(6, 12)
@commands.command()
async def birb(event):
    """Fetch a random birb.

    Image source: r/Birbs
    """
    await get_reddit_image(event, URL_BIRBS_SUBREDDIT_TOP_API, URL_BIRBS_SUBREDDIT_NEW_API)


@commands.cooldown(6, 12)
@commands.command()
async def fox(event):
    """Fetch a random fox.

    Image source: r/foxes
    """
    await get_reddit_image(event, URL_FOX_SUBREDDIT_TOP_API, URL_FOX_SUBREDDIT_NEW_API)


@commands.cooldown(6, 12)
@commands.command()
async def wolf(event):
    """Fetch a random wolf.

    Image source: r/wolves
    """
    await get_reddit_image(event, URL_WOLF_SUBREDDIT_TOP_API, URL_WOLF_SUBREDDIT_NEW_API)


@commands.cooldown(6, 12)
@commands.command()
async def beaver(event):
    """Fetch a random beaver.

    Image source: r/Beavers
    """
    await get_reddit_image(event, URL_BEAVER_SUBREDDIT_TOP_API, URL_BEAVER_SUBREDDIT_NEW_API)


@commands.cooldown(6, 12)
@commands.command()
async def raccoon(event):
    """Fetch a random raccoon.

    Image sources: raccoon.club, r/Raccoons
    """
    use_reddit = secrets.randbelow(2)
    if use_reddit:
        await raccoon.all_commands["reddit"].invoke(event, "")
    else:
        await raccoon.all_commands["club"].invoke(event, "")


@commands.cooldown(6, 12)
@raccoon.command(aliases=["c"])
async def club(event):
    """Fetch a random raccoon.

    Image source: raccoon.club
    """
    response_content = await query(event.processor.session, URL_RACCOON_CLUB_RANDOM_API, "raccoon.club")
    try:
        response_content = json.loads(response_content)
        url = response_content["url"]
        credit = response_content["credit"]
    except Exception as error:
        raise WebAPIInvalidResponse(service="raccoon.club") from error
    await event.reply(url)
    if credit:
        await event.reply(f"Credit: {credit}")


@commands.cooldown(6, 12)
@raccoon.command(aliases=["r"])
async def reddit(event):
    """Fetch a random raccoon.

    Image source: r/Raccoons
    """
    await get_reddit_image(event, URL_RACCOON_SUBREDDIT_TOP_API, URL_RACCOON_SUBREDDIT_NEW_API)    
