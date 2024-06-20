import discord

from modules.modManager import CheckUpdateModStats
from parameters.guildLanguage import guildLanguage


def onMessageDelete(client):
    @client.event
    async def on_message_delete(message):
        if isinstance(message.channel, discord.DMChannel):
            return

        if message.author == client.user and message.channel.name == "wal-i-mods" and message.embeds:
            modEmbed = message.embeds[0]
            for member in message.guild.members:
                if member.name == modEmbed.title and "wal-i-mod" in [role.name for role in member.roles]:
                    modrole = discord.utils.get(
                        message.guild.roles, name="wal-i-mod")
                    if modrole:
                        await member.remove_roles(modrole)
                    return
