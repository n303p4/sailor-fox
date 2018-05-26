#!/usr/bin/env python3

"""A time command."""

import datetime
import pytz
from pytz.exceptions import UnknownTimeZoneError
from sailor import commands

URL = "https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
FORMAT = "%H:%M:%S %Z%z"


@commands.cooldown(6, 12)
@commands.command(aliases=["timein", "tz", "timezone"])
async def time(ctx, *, timezone):
    """A command that fetches the time in a given area."""
    try:
        timezone = pytz.timezone(timezone)
    except UnknownTimeZoneError:
        raise Exception(("Invalid timezone provided. Please refer to "
                         f"<{URL}> for a complete list of timezones."))
    utcmoment = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    localized_datetime = utcmoment.astimezone(timezone)
    message = (f"The time in {timezone.zone} is currently "
               f"{localized_datetime.strftime(FORMAT)}.")
    await ctx.send(message)
