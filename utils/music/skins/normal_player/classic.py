# -*- coding: utf-8 -*-
import itertools
from os.path import basename

import disnake

from utils.music.converters import fix_characters, time_format, get_button_style, music_source_image
from utils.music.models import LavalinkPlayer
from utils.others import PlayerControls


class ClassicSkin:

    __slots__ = ("name", "preview")

    def __init__(self):
        self.name = basename(__file__)[:-3]
        self.preview = "https://i.ibb.co/893S3dJ/image.png"

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

        embed = disnake.Embed(color=color, description="")

        queue_txt = ""

        bar = "https://cdn.discordapp.com/attachments/554468640942981147/1127294696025227367/rainbow_bar3.gif"

        embed_top = disnake.Embed(
            color=color,
            description=f"### [{player.current.title}]({player.current.uri or player.current.search_uri})"
        )
        embed.set_image(url=bar)

        embed_top.set_image(url=bar)

        embed_top.set_thumbnail(url=player.current.thumb)

        if not player.paused:
            (embed_top or embed).set_author(
                name="Currently Playing:",
                icon_url=music_source_image(player.current.info["sourceName"])
            )
        else:
            (embed_top or embed).set_author(
                name="Paused:",
                icon_url="https://cdn.discordapp.com/attachments/480195401543188483/896013933197013002/pause.png"
            )

        if player.current.is_stream:
            duration = "🔴 **⠂ `Livestream`"
        else:
            duration = f"⏰ **⠂** `{time_format(player.current.duration)}`"

        txt = f"{duration}\n" \
              f"👤 **⠂** `{player.current.author}`\n"

        if not player.current.autoplay:
            txt += f"🎧 **⠂** <@{player.current.requester}>\n"
        else:
            try:
                mode = f" [`Recommended`]({player.current.info['extra']['related']['uri']})"
            except:
                mode = "`Recommended`"
            txt += f"> 👍 **⠂** {mode}\n"

        if player.current.playlist_name:
            txt += f"📑 **⠂** [`{fix_characters(player.current.playlist_name, limit=19)}`]({player.current.playlist_url})\n"

        if qsize := len(player.queue):

            if not player.mini_queue_enabled:
                txt += f"🎶 **⠂** `{qsize} song{'s'[:qsize^1]} in queue`\n"
            else:
                queue_txt += "```ansi\n[0;33mUpcoming Songs:[0m```" + "\n".join(
                    f"`{(n + 1):02}) [{time_format(t.duration) if t.duration else '🔴 Livestream'}]` "
                    f"[`{fix_characters(t.title, 29)}`]({t.uri})" for n, t in
                    enumerate(itertools.islice(player.queue, 3))
                )

                if qsize > 3:
                    queue_txt += f"\n`╚══════ And {(t:=qsize - 3)} more song{'s'[:t^1]} ══════╝`"

        elif len(player.queue_autoplay):
            queue_txt += "```ansi\n[0;33mNext song:[0m```" + "\n".join(
                f"`👍⠂{(n + 1):02}) [{time_format(t.duration) if t.duration else '🔴 Livestream'}]` "
                f"[`{fix_characters(t.title, 29)}`]({t.uri})" for n, t in
                enumerate(itertools.islice(player.queue_autoplay, 3))
            )

        if player.command_log:
            txt += f"{player.command_log_emoji} **⠂Last Interaction:** {player.command_log}\n"

        embed.description += txt + queue_txt

        if player.current_hint:
            embed.set_footer(text=f"💡 Hint: {player.current_hint}")
        else:
            embed.set_footer(
                text=str(player),
                icon_url="https://i.ibb.co/QXtk5VB/neon-circle.gif"
            )

        data["embeds"] = [embed_top, embed] if embed_top else [embed]

        data["components"] = [
            disnake.ui.Button(emoji="⏯️", custom_id=PlayerControls.pause_resume, style=get_button_style(player.paused)),
            disnake.ui.Button(emoji="⏮️", custom_id=PlayerControls.back),
            disnake.ui.Button(emoji="⏹️", custom_id=PlayerControls.stop),
            disnake.ui.Button(emoji="⏭️", custom_id=PlayerControls.skip),
            disnake.ui.Button(emoji="<:music_queue:703761160679194734>", custom_id=PlayerControls.queue, disabled=not (player.queue or player.queue_autoplay)),
            disnake.ui.Select(
                placeholder="More options:",
                custom_id="musicplayer_dropdown_inter",
                min_values=0, max_values=1, required=False,
                options=[
                    disnake.SelectOption(
                        label="Add Song", emoji="<:add_music:588172015760965654>",
                        value=PlayerControls.add_song,
                        description="Add a song/playlist to the queue."
                    ),
                    disnake.SelectOption(
                        label="Add to Your Favorites", emoji="💗",
                        value=PlayerControls.add_favorite,
                        description="Add the current song to your favorites."
                    ),
                    disnake.SelectOption(
                        label="Restart Song", emoji="⏪",
                        value=PlayerControls.seek_to_start,
                        description="Go back to the start of the current song."
                    ),
                    disnake.SelectOption(
                        label=f"Volume: {player.volume}%", emoji="🔊",
                        value=PlayerControls.volume,
                        description="Adjust volume."
                    ),
                    disnake.SelectOption(
                        label="Shuffle", emoji="🔀",
                        value=PlayerControls.shuffle,
                        description="Shuffle the queue songs."
                    ),
                    disnake.SelectOption(
                        label="Re-add", emoji="🎶",
                        value=PlayerControls.readd,
                        description="Re-add played songs back to the queue."
                    ),
                    disnake.SelectOption(
                        label="Repeat", emoji="🔁",
                        value=PlayerControls.loop_mode,
                        description="Toggle song/queue repeat."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.nightcore else "Enable") + " nightcore effect", emoji="🇳",
                        value=PlayerControls.nightcore,
                        description="Effect that increases the speed and pitch of the music."
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
    return ClassicSkin()
