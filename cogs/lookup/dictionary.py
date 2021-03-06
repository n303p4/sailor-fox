"""Dictionary lookup command."""

import urllib.parse

from sailor import commands
from sailor.web_exceptions import WebAPIInvalidResponse, WebAPINoResultsFound, WebAPIUnreachable

from sailor_fox.helpers import FancyMessage

BASE_URL_DICTIONARY_API = "https://api.dictionaryapi.dev/api/v2/entries/en/"
MAX_NUM_RESULTS = 10


def generate_search_url(word):
    """Given a word, generate an OwlBot API search URL."""
    word = word.lower()
    url = urllib.parse.urljoin(BASE_URL_DICTIONARY_API, word)
    return url


async def search(session, url):
    """Given a ClientSession and URL, query the URL and return its response content as a JSON."""
    async with session.get(url, timeout=10) as response:
        if response.status != 200:
            raise WebAPIUnreachable(service="dictionaryapi.dev")
        try:
            response_content = await response.json()
        except Exception as error:
            raise WebAPIInvalidResponse(service="dictionaryapi.dev") from error
    return response_content


def generate_parsed_results(response_content, formatter):
    """Given response content from dictionaryapi.dev, generate a list of parsed results."""
    try:
        if not isinstance(response_content, list):
            raise WebAPINoResultsFound(message="No results found for that word.")

        results = []

        for word in response_content:
            meanings = word["meanings"]

            for meaning in meanings:
                for definition in meaning["definitions"]:
                    if len(results) >= MAX_NUM_RESULTS:
                        break
                    description = definition.get("definition")
                    if not description:
                        continue

                    example = definition.get("example")
                    if example:
                        example = formatter.italic(example)
                        description = f"{description}\nExample: {example}"

                    result = {
                        "type": meaning["partOfSpeech"],
                        "description": description
                    }

                    results.append(result)

        if not results:
            raise WebAPINoResultsFound(message="No results found for that word.")

        return results

    except Exception as error:
        raise WebAPIInvalidResponse(service="dictionaryapi.dev") from error


@commands.cooldown(6, 12)
@commands.command()
async def define(event, word: str):
    """Define a word.

    **Example usage**

    * `define cat`
    * `define dog`
    * `define fox`
    """
    url = generate_search_url(word)
    response_content = await search(event.processor.session, url)
    results = generate_parsed_results(response_content, event.f)

    message = FancyMessage(event.f, sep="\n\n")

    for result in results:
        message.add_field(name=result["type"], value=result["description"], sep="\n")

    await event.reply(message)
