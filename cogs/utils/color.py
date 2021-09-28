"""Contains a cog that fetches colors."""

# pylint: disable=C0103

import colorsys
import secrets

import colour
from sailor import commands
from sailor.exceptions import UserInputError
import webcolors

from sailor_fox.helpers import FancyMessage

BASE_URL_COLOR_API = "https://www.colourlovers.com/img/{0}/{1}/{2}/"
BASE_URL_TINEYE_MULTICOLR = "https://labs.tineye.com/multicolr/#colors={0};weights=100"
BASE_URL_COLOR_HEX = "https://www.color-hex.com/color/{0}"
BASE_URL_ENCYCOLORPEDIA = "https://encycolorpedia.com/{0}"


def rgb_to_hsv(red, green, blue):
    """Convert an RGB tuple to an HSV tuple."""
    hue, saturation, value = colorsys.rgb_to_hsv(red/255, green/255, blue/255)
    return int(hue*360), int(saturation*100), int(value*100)


def rgb_to_hls(red, green, blue):
    """Convert an RGB tuple to an HLS tuple."""
    hue, lightness, saturation = colorsys.rgb_to_hls(red/255, green/255, blue/255)
    return int(hue*360), int(lightness*100), int(saturation*100)


def color_from_string(color):
    """Given a string, get color info."""
    try:
        color = webcolors.name_to_hex(color)
    except (ValueError, AttributeError):
        pass
    try:
        if not color:
            color = "#" + hex(secrets.randbelow(16777216)).replace("0x", "", 1)
        color = colour.Color(color)
    except Exception as error:
        raise UserInputError((
            "Not a valid color. Color must either be:\n"
            "A) In hex format and between FFFFFF and 000000, or\n"
            "B) A named CSS color (e.g. red or lightsteelblue)."
        )) from error
    return color


@commands.cooldown(6, 12)
@commands.command(aliases=["simplecolour", "scolor", "scolour"])
async def simplecolor(event, *, color: str = None):
    """Display a color, without detailed info. Accepts CSS color names and hex input.

    * `color` - Either a CSS color or hex input.
    """
    color = color_from_string(color)

    message = []

    message.append(event.f.bold(color.hex))
    message.append(BASE_URL_COLOR_API.format(color.hex.lstrip("#"), 88, 88))

    await event.reply("\n".join(message))


@commands.cooldown(6, 12)
@commands.command(name="color", aliases=["colour"])
async def color_(event, *, color: str = None):
    """Display a color, with detailed info. Accepts CSS color names and hex input.

    * `color` - Either a CSS color or hex input.
    """
    color = color_from_string(color)
    color_hex_value = color.hex.lstrip("#")

    message = FancyMessage(event.f)

    color_as_rgb = tuple(round(255*x) for x in color.rgb)
    color_as_rgba = color_as_rgb + (1.0,)
    message.add_field(name="RGB", value=f"rgb{color_as_rgb}")
    message.add_field(name="RGBA", value=f"rgba{color_as_rgba}")
    message.add_field(name="HSV", value=rgb_to_hsv(*color_as_rgb))
    message.add_field(name="HLS", value=rgb_to_hls(*color_as_rgb))
    message.add_field(name="Hex", value=f"#{color_hex_value}")
    message.add_field(name="Images", value=event.f.no_embed_link(BASE_URL_TINEYE_MULTICOLR.format(color_hex_value)))

    information_links = (f"{event.f.no_embed_link(BASE_URL_COLOR_HEX.format(color_hex_value))}\n"
                         f"{event.f.no_embed_link(BASE_URL_ENCYCOLORPEDIA.format(color_hex_value))}")
    message.add_line(event.f.bold("Information:"))
    message.add_line(information_links)

    message.add_line(event.f.bold("Note:"))
    message.add_line("HSV and HLS may be slightly wrong due to floating point errors.")

    image_url = BASE_URL_COLOR_API.format(color_hex_value, 88, 88)
    message.add_line(image_url)

    await event.reply(message)
