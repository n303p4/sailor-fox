"""A time command."""

import datetime
import pytz
from pytz.exceptions import UnknownTimeZoneError
from sailor import commands, exceptions

URL = "https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
FORMAT = "%-I:%M:%S %p %Z (UTC%z)"
CONTINENTS = ["Africa/", "America/", "America/Argentina/", "America/Indiana/", "America/Kentucky/",
              "Antarctica/", "Asia/", "Australia/", "Europe/", "Indian/", "Pacific/", "Etc/", ""]


@commands.cooldown(6, 12)
@commands.command(aliases=["timein", "tz", "timezone"])
async def time(event, *, location: str):
    """
    A command that fetches the time in a given area using TZ database names.

    Tries to do some guesswork to accommodate simplified inputs.

    Example usage:
    * time Europe/Berlin
    * time UTC
    * time buenos aires
    """
    try:
        timezone = location.replace(" ", "_")
        if not "/" in timezone:
            if timezone.upper() != timezone:
                timezone = timezone.title()
            for continent in CONTINENTS:
                try:
                    timezone = pytz.timezone(f"{continent}{timezone}")
                except UnknownTimeZoneError:
                    continue
                else:
                    break
            if isinstance(timezone, str):
                raise UnknownTimeZoneError()
        else:
            timezone = pytz.timezone(location)
    except UnknownTimeZoneError as error:
        raise exceptions.UserInputError((
            "Could not determine TZ database name from input. Please refer to "
            f"{event.f.no_embed_link(URL)} for a complete list of TZ database names. "
            "(The part before the / is usually not needed)"
        )) from error
    utcmoment = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    localized_datetime = utcmoment.astimezone(timezone)
    human_readable_location = timezone.zone.split("/")[-1].replace("_", " ")
    message = (f"The time in {human_readable_location} is currently "
               f"{localized_datetime.strftime(FORMAT)}.")
    await event.reply(message)
