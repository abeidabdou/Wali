from parameters.waliSetupManager import WaliSetupManager
import discord


async def logActions(log_action, guild):

    logsChannel = await WaliSetupManager(guild).get_or_create_logs_channel()

    async def send_single_message(msg):
        await logsChannel.send(embed=discord.Embed(description=msg))

    if isinstance(log_action, list):
        if isinstance(log_action[0], discord.Embed):
           MAX_EMBEDS_PER_MESSAGE = 9
           for i in range(0, len(log_action), MAX_EMBEDS_PER_MESSAGE):
                await logsChannel.send(embeds=log_action[i:i+MAX_EMBEDS_PER_MESSAGE])
        else:
            await send_single_message(log_action)
    else:
        await send_single_message(log_action)
