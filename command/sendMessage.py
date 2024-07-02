import re
import discord


async def sendMessage(ctx_or_message, messageToSend):

    async def send_single_message(msg):
        match = None
        if not isinstance(msg, list):
           match = re.search(r'sendMessage\("([^"]*)"\)', msg)
        else:
            msg = '\n'.join(msg)
           
        if match:
            msg = match.group(1)
        if isinstance(ctx_or_message, discord.Message):
            return
        if ctx_or_message.channel.name in ['wal-i-mods-channel', 'wal-i']:
            await ctx_or_message.followup.send(embed=discord.Embed(description=msg))
        else:
            await ctx_or_message.followup.send(embed=discord.Embed(description=msg), ephemeral=True)

    await send_single_message(messageToSend)
