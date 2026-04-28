# -*- coding: utf-8 -*-
from __future__ import annotations

import datetime
import json
import re
import traceback
from typing import Union, TYPE_CHECKING

import disnake

if TYPE_CHECKING:
    pass

URL_REG = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|%[0-9a-fA-F][0-9a-fA-F])+')
YOUTUBE_VIDEO_REG = re.compile(r"(https?://)?(www\.|music\.)?youtube\.(com|nl)/watch\?v=([-\w]+)")

replaces = [
    ('&quot;', '"'),
    ('&amp;', '&'),
    ('(', '\u0028'),
    (')', '\u0029'),
    ('[', '【'),
    (']', '】'),
    ("  ", " "),
    ("*", '"'),
    ("_", ' '),
    ("{", "\u0028"),
    ("}", "\u0029"),
    ("`", "'")
]


async def google_search(bot, query: str, *, max_entries: int = 20) -> list:

    try:
        async with bot.session.get(
                "https://suggestqueries.google.com/complete/search",
                headers={'User-Agent': bot.pool.current_useragent} if bot.pool.current_useragent else None,
                params={
                    'client': 'youtube',
                    'q': query,
                    'ds': 'yt',
                    'hl': 'en'
                }
        ) as r:

            text = await r.text()
            json_text = text[text.find("(") + 1:text.rfind(")")]
            return [result[0] for result in json.loads(json_text)[1][:max_entries]]
    except:
        traceback.print_exc()
        return []


def get_button_style(enabled: bool, red=True):
    if enabled:
        if red:
            return disnake.ButtonStyle.red
        return disnake.ButtonStyle.green
    return disnake.ButtonStyle.grey


def fix_characters(text: str, limit: int = 0):
    for r in replaces:
        old, new = r
        text = text.replace(old, new)

    if limit:
        text = f"{text[:limit]}..." if len(text) > limit else text

    return text


def time_format(milliseconds: Union[int, float], use_names: bool = False) -> str:
    minutes, seconds = divmod(int(milliseconds / 1000), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    if use_names:

        times = []

        for time_, name in (
                (days, "day"),
                (hours, "hour"),
                (minutes, "minute"),
                (seconds, "second")
        ):
            if not time_:
                continue

            times.append(f"{time_} {name}" + ("s" if time_ > 1 else ""))

        try:
            last_time = times.pop()
        except IndexError:
            last_time = None
            times = ["1 second"]

        strings = ", ".join(t for t in times)

        if last_time:
            strings += f" and {last_time}" if strings else last_time

    else:

        strings = f"{minutes:02d}:{seconds:02d}"

        if hours:
            strings = f"{hours}:{strings}"

        if days:
            strings = (f"{days} days" if days > 1 else f"{days} day") + (f", {strings}" if strings != "00:00" else "")

    return strings


time_names = ["seconds", "minutes", "hours"]


def string_to_seconds(time):
    try:

        times = reversed([i for i in time.replace(" ", ":").split(':') if i.isdigit()])
        time_dict = {}

        for n, t in enumerate(times):
            time_dict[time_names[n]] = int(t)

        return datetime.timedelta(**time_dict).total_seconds()

    except:
        return


def percentage(part, whole):
    return int((part * whole) / 100.0)

sources = {
    "deezer": "https://iili.io/d1Kjip1.png",
    "soundcloud": "https://iili.io/d1KjPkP.md.png",
    "spotify": "https://iili.io/d1KVvlS.png",
    "youtube": "https://iili.io/d1KjLTF.md.png",
    "applemusic": "https://iili.io/d1Kj6YB.md.png",
    "twitch": "https://cdn3.iconfinder.com/data/icons/popular-services-brands-vol-2/512/twitch-512.png",
    "jiosaavn": "https://iili.io/d1KjUEx.png",
    "tidal": "https://iili.io/d1KjgrQ.png",
    "youtubemusic": "https://iili.io/d1Kj42V.png",
    "last.fm": "https://cdn.discordapp.com/emojis/1278883704097341541.png",
}

def music_source_image(sourcename):
    return sources.get(
        sourcename,
        "https://cdn.discordapp.com/attachments/480195401543188483/895862881105616947/music_equalizer.gif"
    )


perms_translations = {
    "add_reactions": "Add Reactions",
    "administrator": "Administrator",
    "attach_files": "Attach Files",
    "ban_members": "Ban Members",
    "change_nickname": "Change Nickname",
    "connect": "Connect to Voice Channel",
    "create_instant_invite": "Create Instant Invite",
    "create_private_threads": "Create Private Threads",
    "create_public_threads": "Create Public Threads",
    "deafen_members": "Deafen Members",
    "embed_links": "Embed Links",
    "kick_members": "Kick Members",
    "manage_channels": "Manage Channels",
    "manage_emojis_and_stickers": "Manage Emojis and Stickers",
    "manage_events": "Manage Events",
    "manage_guild": "Manage Server",
    "manage_messages": "Manage Messages",
    "manage_nicknames": "Manage Nicknames",
    "manage_roles": "Manage Roles",
    "manage_threads": "Manage Threads",
    "manage_webhooks": "Manage Webhooks",
    "mention_everyone": "Mention @everyone and @here",
    "moderate_members": "Moderate Members",
    "move_members": "Move Members",
    "mute_members": "Mute Members",
    "priority_speaker": "Priority Speaker",
    "read_message_history": "Read Message History",
    "read_messages": "Read Messages",
    "request_to_speak": "Request to Speak",
    "send_messages": "Send Messages",
    "send_messages_in_threads": "Send Messages in Threads",
    "send_tts_messages": "Send Text-to-Speech Messages",
    "speak": "Speak in Voice Channel",
    "stream": "Stream",
    "use_application_commands": "Use Application/Bot Commands",
    "use_embedded_activities": "Use Embedded Activities",
    "use_external_emojis": "Use External Emojis",
    "use_external_stickers": "Use External Stickers",
    "use_voice_activation": "Use Voice Activation Detection",
    "view_audit_log": "View Audit Log",
    "view_channel": "View Channel",
    "view_guild_insights": "View Server Insights"
}
