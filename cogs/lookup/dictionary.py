#!/usr/bin/env python3

"""Dictionary lookup command."""

import re
import urllib.parse

import async_timeout
from sailor import commands
from sailor.web_exceptions import WebAPIInvalidResponse, WebAPINoResultsFound, WebAPIUnreachable

BASE_URL_OWL_API = "https://owlbot.info/api/v1/dictionary/{0}{1}"
MAX_NUM_RESULTS = 5


def generate_search_url(word):
    """Given a word, generate an OwlBot API search URL."""
    word = word.lower()
    params = "?{0}".format(urllib.parse.urlencode({"format": "json"}))
    url = BASE_URL_OWL_API.format(word, params)
    return url


async def search(session, url):
    """Given a ClientSession and URL, query the URL and return its response content as a JSON."""
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            if response.status == 200:
                try:
                    response_content = await response.json()
                except Exception:
                    raise WebAPIInvalidResponse(service="OwlBot")
            else:
                raise WebAPIUnreachable(service="OwlBot")

    return response_content


def generate_parsed_results(response_content):
    """Given response content from OwlBot, generate a list of parsed results."""
    try:
        if not response_content:
            raise WebAPINoResultsFound(message="No results found for that word.")

        num_results_to_display = min(MAX_NUM_RESULTS, len(response_content))
        results = []

        for index in range(0, num_results_to_display):
            response_result = response_content[index]
            definition = response_result.get('defenition')
            description = re.sub("<.*?>|\u00E2|\u0080|\u0090", "",
                                 definition.capitalize())
            example = response_result.get('example')

            if example:
                example = re.sub("<.*?>|\u00E2|\u0080|\u0090", "",
                                 example.capitalize())
                example = f"*{example}*"
                description = f"{description}\nExample: {example}"

            result = {
                "type": response_result["type"],
                "description": description
            }

            results.append(result)

        return results

    except Exception:
        raise WebAPIInvalidResponse(service="OwlBot")


@commands.cooldown(6, 12)
@commands.command()
async def define(ctx, word: str):
    """Define a word.

    Example usage:
    * define cat
    * define dog
    * define fox
    """
    url = generate_search_url(word)
    response_content = await search(ctx.bot.session, url)
    results = generate_parsed_results(response_content)

    combined_results = []

    for result in results:
        combined_result = f"{ctx.f.bold(result['type'])}\n{result['description']}"
        combined_results.append(combined_result)

    await ctx.send("\n\n".join(combined_results))
