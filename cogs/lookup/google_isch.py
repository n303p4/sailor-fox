"""This cog contains an image query command."""

import secrets
from urllib.parse import urljoin, urlencode, urlparse, parse_qs

from bs4 import BeautifulSoup

from sailor import commands
from sailor.web_exceptions import WebAPIUnreachable, WebAPINoResultsFound, WebAPIInvalidResponse

BASE_URL_GOOGLE = "https://www.google.com"
BASE_URL_GOOGLE_ISCH = "https://www.google.com/search?{0}"
WEBSITE_TEXT = "Website for this image"
USER_AGENT = ("Opera/9.80 (J2ME/MIDP; Opera Mini/(Windows; U; Windows NT 5.1; en-US) AppleWebKit/23.411; U; en) "
              "Presto/2.5.25 Version/10.54")
SEARCH_HEADERS = {"User-Agent": USER_AGENT}


async def _google_isch_get_one(session, query: str, search_headers: dict=None):
    """Google image search function that gets a random image result."""

    if not search_headers:
        search_headers = SEARCH_HEADERS

    params = urlencode({"tbm": "isch", "q": query})
    url = BASE_URL_GOOGLE_ISCH.format(params)
    async with session.get(url, headers=search_headers, timeout=10) as response:
        if response.status >= 400:
            raise WebAPIUnreachable(service="Google Images")
        try:
            xml = await response.text()
            soup = BeautifulSoup(xml, features="lxml")
        except Exception as error:
            raise WebAPIInvalidResponse(service="Google Images") from error
        results = soup.find_all("a", href=lambda h: h.startswith("/imgres"))
        if not results:
            raise WebAPINoResultsFound(message="No images found.")
        try:
            result = secrets.choice(results)["href"]
        except Exception as error:
            raise WebAPIInvalidResponse(service="Google Images") from error
        return urljoin(BASE_URL_GOOGLE, result)


async def _google_isch_handle_one(session, url, search_headers: dict=None):
    """Google image search function that parses an individual result."""

    if not search_headers:
        search_headers = SEARCH_HEADERS

    async with session.get(url, headers=search_headers, timeout=10) as response:
        if response.status >= 400:
            raise WebAPIUnreachable(service="Google Images")
        try:
            xml = await response.text()
            soup = BeautifulSoup(xml, features="lxml")
            thumbnail = soup.find("a", id="thumbnail", href=True)
            website_link = soup.find("a", href=True, text=WEBSITE_TEXT)
            image_url = thumbnail["href"]
            website_url = parse_qs(urlparse(website_link["href"]).query)["q"][0]
            return image_url, website_url
        except Exception as error:
            raise WebAPIInvalidResponse(service="Google Images") from error


@commands.cooldown(6, 12)
@commands.command(aliases=["img", "gimage", "gimg"])
async def image(event, *, query: str):
    """Get a random image off the Internet using Google Images.

    * `query` - A string to be used in the search criteria.
    """
    search_result_url = await _google_isch_get_one(event.processor.session, query, SEARCH_HEADERS)
    image_url, website_url = await _google_isch_handle_one(event.processor.session, search_result_url, SEARCH_HEADERS)
    message = [
        event.f.bold("Website: ") + event.f.no_embed_link(website_url),
        event.f.bold("Full-size image: ") + image_url,
        "Powered (but not endorsed) by Google Images"
    ]
    await event.reply("\n".join(message))
