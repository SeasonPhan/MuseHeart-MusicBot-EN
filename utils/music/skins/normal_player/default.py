# -*- coding: utf-8 -*-
import datetime
import itertools
from os.path import basename

import disnake

from utils.music.converters import fix_characters, time_format, get_button_style, music_source_image
from utils.music.models import LavalinkPlayer
from utils.others import PlayerControls


class DefaultSkin:

    __slots__ = ("name", "preview")

    def __init__(self):
        self.name = basename(__file__)[:-3]
        self.preview = "https://i.ibb.co/4PkWyqb/image.png"

    def setup_features(self, player: LavalinkPlayer):
        player.mini_queue_feature = True
        player.controller_mode = True
        player.auto_update = 0
        player.hint_rate = player.bot.config["HINT_RATE"]
        player.static = False

    def load(self, player: LavalinkPlayer) -> dict:

        data = {
            "content": None,
            "embeds": []
        }

        color = player.bot.get_color(player.guild.me)

        embed = disnake.Embed(color=color)
        embed_queue = None
        vc_txt = ""

        if not player.paused:
            embed.set_author(
                name="Currently Playing:",
                icon_url=music_source_image(player.current.info["sourceName"])
            )

        else:
            embed.set_author(
                name="Paused:",
                icon_url="https://cdn.discordapp.com/attachments/480195401543188483/896013933197013002/pause.png"
            )

        if player.current_hint:
            embed.set_footer(text=f"💡 Hint: {player.current_hint}")
        else:
            embed.set_footer(
                text=str(player),
                icon_url="https://i.ibb.co/QXtk5VB/neon-circle.gif"
            )

        player.mini_queue_feature = True

        duration = "> -# 🔴 **⠂** `Livestream`\n" if player.current.is_stream else \
            (f"> -# ⏰ **⠂** `{time_format(player.current.duration)} [`" +
            f"<t:{int((disnake.utils.utcnow() + datetime.timedelta(milliseconds=player.current.duration - player.position)).timestamp())}:R>`]`\n"
            if not player.paused else '')

        txt = f"-# [`{player.current.single_title}`]({player.current.uri or player.current.search_uri})\n\n" \
              f"{duration}" \
              f"> -# 👤 **⠂** {player.current.authors_md}"

        if not player.current.autoplay:
            txt += f"\n> -# ✋ **⠂** <@{player.current.requester}>"
        else:
            try:
                mode = f" [`Recommended`]({player.current.info['extra']['related']['uri']})"
            except:
                mode = "`Recommended`"
            txt += f"\n> -# 👍 **⠂** {mode}"

        if player.current.track_loops:
            txt += f"\n> -# 🔂 **⠂** `Remaining repetitions: {player.current.track_loops}`"

        if player.loop:
            if player.loop == 'current':
                e = '🔂'; m = 'Current Song'
            else:
                e = '🔁'; m = 'Queue'
            txt += f"\n> -# {e} **⠂** `Repetition: {m}`"

        if player.current.album_name:
            txt += f"\n> -# 💽 **⠂** [`{fix_characters(player.current.album_name, limit=36)}`]({player.current.album_url})"

        if player.current.playlist_name:
            txt += f"\n> -# 📑 **⠂** [`{fix_characters(player.current.playlist_name, limit=36)}`]({player.current.playlist_url})"

        if (qlenght:=len(player.queue)) and not player.mini_queue_enabled:
            txt += f"\n> -# 🎶 **⠂** `{qlenght} song{'s'[:qlenght^1]} in queue`"

        if player.keep_connected:
            txt += "\n> -# ♾️ **⠂** `24/7 mode activated`"

        txt += f"{vc_txt}\n"

        bar = "https://cdn.discordapp.com/attachments/554468640942981147/1127294696025227367/rainbow_bar3.gif"

        if player.command_log:
            txt += f"```ansi\n [34;1mLast Interaction:[0m```**┕ {player.command_log_emoji} ⠂**{player.command_log}\n"

        if player.mini_queue_enabled:

            if len(player.queue):

                queue_txt = "\n".join(
                    f"-# `{(n + 1):02}) [{time_format(t.duration) if not t.is_stream else '🔴 Livestream'}]` [`{fix_characters(t.title, 21)}`]({t.uri})"
                    for n, t in (enumerate(itertools.islice(player.queue, 3)))
                )

                embed_queue = disnake.Embed(title=f"Songs in queue: {qlenght}", color=color,
                                            description=f"\n{queue_txt}")

                if not player.loop and not player.keep_connected and not player.paused:

                    queue_duration = 0

                    for t in player.queue:
                        if not t.is_stream:
                            queue_duration += t.duration

                    embed_queue.description += f"\n-# `[⌛ Songs end` <t:{int((disnake.utils.utcnow() + datetime.timedelta(milliseconds=(queue_duration + (player.current.duration if not player.current.is_stream else 0)) - player.position)).timestamp())}:R> `⌛]`"

                embed_queue.set_image(url=bar)

            elif len(player.queue_autoplay):
                queue_txt = "\n".join(
                    f"-# `👍⠂{(n + 1):02}) [{time_format(t.duration) if not t.is_stream else '🔴 Livestream'}]` [`{fix_characters(t.title, 20)}`]({t.uri})"
                    for n, t in (enumerate(itertools.islice(player.queue_autoplay, 3)))
                )
                embed_queue = disnake.Embed(title="Next recommended songs:", color=color,
                                            description=f"\n{queue_txt}")
                embed_queue.set_image(url=bar)

        embed.description = txt
        embed.set_image(url=bar)
        embed.set_thumbnail(url=player.current.thumb)

        data["embeds"] = [embed_queue, embed] if embed_queue else [embed]

        data["components"] = [
            disnake.ui.Button(emoji="⏯️", custom_id=PlayerControls.pause_resume, style=get_button_style(player.paused)),
            disnake.ui.Button(emoji="⏮️", custom_id=PlayerControls.back),
            disnake.ui.Button(emoji="⏹️", custom_id=PlayerControls.stop),
            disnake.ui.Button(emoji="⏭️", custom_id=PlayerControls.skip),
            disnake.ui.Button(emoji="<:music_queue:703761160679194734>", custom_id=PlayerControls.queue, disabled=not (player.queue or player.queue_autoplay)),
            disnake.ui.Select(
                placeholder="More options:",
                custom_id="musicplayer_dropdown_inter",
                min_values=0, max_values=1, required = False,
                options=[
                    disnake.SelectOption(
                        label="Add music", emoji="<:add_music:588172015760965654>",
                        value=PlayerControls.add_song,
                        description="Add a song/playlist to the queue."
                    ),
                    disnake.SelectOption(
                        label="Add to your favorites", emoji="💗",
                        value=PlayerControls.add_favorite,
                        description="Add the current song to your favorites."
                    ),
                    disnake.SelectOption(
                        label="Start from beginning", emoji="⏪",
                        value=PlayerControls.seek_to_start,
                        description="Go back to the beginning of the current song."
                    ),
                    disnake.SelectOption(
                        label=f"Volume: {player.volume}%", emoji="🔊",
                        value=PlayerControls.volume,
                        description="Adjust volume."
                    ),
                    disnake.SelectOption(
                        label="Shuffle", emoji="🔀",
                        value=PlayerControls.shuffle,
                        description="Shuffle songs in the queue."
                    ),
                    disnake.SelectOption(
                        label="Re-add", emoji="🎶",
                        value=PlayerControls.readd,
                        description="Re-add played songs back to the queue."
                    ),
                    disnake.SelectOption(
                        label="Loop", emoji="🔁",
                        value=PlayerControls.loop_mode,
                        description="Enable/Disable song/queue looping."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.nightcore else "Enable") + " Nightcore effect", emoji="🇳",
                        value=PlayerControls.nightcore,
                        description="Effect that increases speed and pitch of the song."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.autoplay else "Enable") + " autoplay", emoji="🔄",
                        value=PlayerControls.autoplay,
                        description="Automatically add music when the queue is empty."
                    ),
                    disnake.SelectOption(
                        label="Last.fm scrobble", emoji="<:Lastfm:1278883704097341541>",
                        value=PlayerControls.lastfm_scrobble,
                        description="Enable/disable scrobbling/logging of songs on your last.fm account."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.restrict_mode else "Enable") + " restricted mode", emoji="🔐",
                        value=PlayerControls.restrict_mode,
                        description="Only DJ's/Staff can use restricted commands."
                    ),
                ]
            ),
        ]

        if player.current.ytid and player.node.lyric_support:
            data["components"][5].options.append(
                disnake.SelectOption(
                    label= "View lyrics", emoji="📃",
                    value=PlayerControls.lyrics,
                    description="Get lyrics of current music."
                )
            )


        if player.mini_queue_feature:
            data["components"][5].options.append(
                disnake.SelectOption(
                    label="Player Mini-queue", emoji="<:music_queue:703761160679194734>",
                    value=PlayerControls.miniqueue,
                    description="Toggle the player's mini-queue."
                )
            )

        if isinstance(player.last_channel, disnake.VoiceChannel):
            data["components"][5].options.append(
                disnake.SelectOption(
                    label="Automatic status", emoji="📢",
                    value=PlayerControls.set_voice_status,
                    description="Set up automatic voice channel status."
                )
            )

        if not player.has_thread:
            data["components"][5].options.append(
                disnake.SelectOption(
                    label="Song-Request Thread", emoji="💬",
                    value=PlayerControls.song_request_thread,
                    description="Create a temporary thread/chat to request songs using just the name/link."
                )
            )

        return data

def load():
    return DefaultSkin()
