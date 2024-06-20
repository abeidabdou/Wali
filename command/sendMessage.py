import discord

async def sendMessage(ctx_or_message, messageToSend):
    
    if isinstance(ctx_or_message, discord.Message):
        return

    if ctx_or_message.channel.name == 'wal-i-mods-channel' or ctx_or_message.channel.name == 'wal-i':
        await ctx_or_message.followup.send(f"```{messageToSend}```")
        return
    await ctx_or_message.followup.send(f"```{messageToSend}```", ephemeral=True)