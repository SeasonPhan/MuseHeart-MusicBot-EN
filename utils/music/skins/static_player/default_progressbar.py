# -*- coding: utf-8 -*-
import datetime
import itertools
from os.path import basename

import disnake

from utils.music.converters import fix_characters, time_format, get_button_style, music_source_image
from utils.music.models import LavalinkPlayer
from utils.others import ProgressBar, PlayerControls


class DefaultProgressbarStaticSkin:

    __slots__ = ("name", "preview")

    def __init__(self):
        self.name = basename(__file__)[:-3] + "_static"
        self.preview = "https://cdn.discordapp.com/attachments/554468640942981147/1047187414176759860/progressbar_static_skin.png"

    def setup_features(self, player: LavalinkPlayer):
        player.mini_queue_feature = False
        player.controller_mode = True
        player.auto_update = 15
        player.hint_rate = player.bot.config["HINT_RATE"]
        player.static = True

    def load(self, player: LavalinkPlayer) -> dict:

        data = {
            "content": None,
            "embeds": []
        }

        embed = disnake.Embed(color=player.bot.get_color(player.guild.me))
        embed_queue = None

        if not player.paused:
            emoji = "▶️"
            embed.set_author(
                name="Currently Playing:",
                icon_url=music_source_image(player.current.info["sourceName"])
            )
        else:
            emoji = "⏸️"
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

        if player.current.is_stream:
            duration = "```ansi\n🔴 [31;1m Livestream[0m```"
        else:

            progress = ProgressBar(
                player.position,
                player.current.duration,
                bar_count=17
            )

            duration = f"```ansi\n[34;1m[{time_format(player.position)}] {('='*progress.start)}[0m🔴️[36;1m{'-'*progress.end} " \
                       f"[{time_format(player.current.duration)}][0m```\n"

        vc_txt = ""
        queue_img = ""

        txt = f"[`{player.current.single_title}`]({player.current.uri or player.current.search_uri})\n\n" \
              f"> 💠 **⠂By:** {player.current.authors_md}"

        if not player.current.autoplay:
            txt += f"\n> ✋ **⠂Requested by:** <@{player.current.requester}>"
            try:
                vc_txt = f"\n> *️⃣ **⠂Voice Channel:** {player.guild.me.voice.channel.mention}"
            except AttributeError:
                pass

        if player.current.track_loops:
            txt += f"\n> 🔂 **⠂Remaining Loops:** `{player.current.track_loops}`"

        if player.loop:
            if player.loop == 'current':
                e = '🔂'
                m = 'Current Song'
            else:
                e = '🔁'
                m = 'Queue'
            txt += f"\n> {e} **⠂Loop Mode:** `{m}`"

        if player.current.album_name:
            txt += f"\n> 💽 **⠂Album:** [`{fix_characters(player.current.album_name, limit=20)}`]({player.current.album_url})"

        if player.current.playlist_name:
            txt += f"\n> 📑 **⠂Playlist:** [`{fix_characters(player.current.playlist_name, limit=20)}`]({player.current.playlist_url})"

        if player.keep_connected:
            txt += "\n> ♾️ **⠂24/7 Mode:** `Enabled`"

        txt += f"{vc_txt}\n"

        if player.command_log:
            txt += f"> {player.command_log_emoji} **⠂Last Interaction:** {player.command_log}\n"

        if player.current.autoplay:
            try:
                mode = f" [`autoplay`]({player.current.info['extra']['related']['uri']})"
            except:
                mode = "`autoplay`"
            txt += f"\n`Currently using` {mode} `while waiting for a member of the channel` {player.guild.me.voice.channel.mention} `to add new songs.`\n"

        txt += duration

        if qlenght:=len(player.queue):

            queue_txt = "\n".join(
                f"`{(n + 1):02}) [{time_format(t.duration) if not t.is_stream else '🔴 Livestream'}]` [`{fix_characters(t.title, 33)}`]({t.uri})"
                for n, t in (enumerate(itertools.islice(player.queue, 20)))
            )

            embed_queue = disnake.Embed(title=f"Songs in Queue: {qlenght}", color=player.bot.get_color(player.guild.me),
                                        description=f"\n{queue_txt}")

            if not player.loop and not player.keep_connected and not player.paused and not player.current.is_stream:

                queue_duration = 0

                for t in player.queue:
                    if not t.is_stream:
                        queue_duration += t.duration

                embed_queue.description += f"\n`[⌛ Songs end` <t:{int((disnake.utils.utcnow() + datetime.timedelta(milliseconds=(queue_duration + (player.current.duration if not player.current.is_stream else 0)) - player.position)).timestamp())}:R> `⌛]`"

            embed_queue.set_image(url=queue_img)

        embed.description = txt
        embed.set_image(url=player.current.thumb)

        data["embeds"] = [embed_queue, embed] if embed_queue else [embed]

        data["components"] = [
            disnake.ui.Button(emoji="⏯️", custom_id=PlayerControls.pause_resume, style=get_button_style(player.paused)),
            disnake.ui.Button(emoji="⏮️", custom_id=PlayerControls.back),
            disnake.ui.Button(emoji="⏹️", custom_id=PlayerControls.stop),
            disnake.ui.Button(emoji="⏭️", custom_id=PlayerControls.skip),
            disnake.ui.Button(emoji="<:music_queue:703761160679194734>", custom_id=PlayerControls.queue, disabled=not player.queue),
            disnake.ui.Select(
                placeholder="More options:",
                custom_id="musicplayer_dropdown_inter",
                min_values=0, max_values=1,
                options=[
                    disnake.SelectOption(
                        label="Add music", emoji="<:add_music:588172015760965654>",
                        value=PlayerControls.add_song,
                        description="Add a song/playlist to the queue."
                    ),
                    disnake.SelectOption(
                        label="Add favorite to queue", emoji="⭐",
                        value=PlayerControls.enqueue_fav,
                        description="Add one of your favorites to the queue."
                    ),
                    disnake.SelectOption(
                        label="Add to your favorites", emoji="💗",
                        value=PlayerControls.add_favorite,
                        description="Add the current song to your favorites."
                    ),
                    disnake.SelectOption(
                        label="Play from start", emoji="⏪",
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
                        description="Enable/Disable song/queue loop."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.nightcore else "Enable") + " nightcore effect", emoji="🇳",
                        value=PlayerControls.nightcore,
                        description="Effect that increases speed and pitch of the music."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.autoplay else "Enable") + " autoplay", emoji="🔄",
                        value=PlayerControls.autoplay,
                        description="System for automatic addition of music when the queue is empty."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.restrict_mode else "Enable") + " restrict mode", emoji="🔐",
                        value=PlayerControls.restrict_mode,
                        description="Only DJ's/Staff's can use restricted commands."
                    ),
                ]
            ),
        ]

        if isinstance(player.last_channel, disnake.VoiceChannel):
            txt = "Disable" if player.stage_title_event else "Enable"
            data["components"][5].options.append(
                disnake.SelectOption(
                    label= f"{txt} automatic status", emoji="📢",
                    value=PlayerControls.stage_announce,
                    description=f"{txt} automatic status of the voice channel."
                )
            )

        if not player.static and not player.has_thread:
            data["components"][5].options.append(
                disnake.SelectOption(
                    label="Song-Request Thread", emoji="💬",
                    value=PlayerControls.song_request_thread,
                    description="Create a temporary thread/conversation to request songs using just the name/link."
                )
            )

        try:
            if isinstance(player.text_channel.parent, disnake.ForumChannel):
                data["content"] = f"`{emoji} {fix_characters(player.current.title, 50)}`"
        except:
            pass

        return data

def load():
    return DefaultProgressbarStaticSkin()
