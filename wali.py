import discord
import os
from ai_studio_api_call import generate_instructions
import re
from events.onDeleteMessage import onMessageDelete
from events.onMessage import onMessage
from modules.modManager import ModCommandsManager
from parameters.guildLanguage import guildLanguage
from parameters.waliSetupManager import WaliSetupManager
from discord import app_commands
from dotenv import load_dotenv
from command.loadCommand import load_command
import json

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def callCommand(ctx, command_name, command_args):
    command_func = await load_command(command_name)
    await command_func(ctx, command_args)

@tree.command(description="Invoke Wali")
async def wal_i(ctx, message: str):

    wali_mods_role_name = 'wal-i-mod'
    language = guildLanguage(ctx.guild)

    if ctx.user.id == ctx.guild.owner_id or wali_mods_role_name in [role.name for role in ctx.user.roles]:

        if ctx.channel.name != 'wal-i-mods-channel' and ctx.channel.name != 'wal-i':
            await ctx.response.send_message(f"```{message}```", ephemeral=True)
        else:
            await ctx.response.send_message(f"```{message}```")

        response = await generate_instructions(f"{message}")

        match = re.match(r'<(\w+)', response.text)
        if match:
            command_name = match.group(1)
            response_text = re.sub(r'[<>]', '', response.text)
            await callCommand(ctx, command_name, response_text)
    else:
        await ctx.response.defer(ephemeral=True)
        messageToSend = f"```{language['command_access_no']}```"
        await callCommand(ctx, "sendMessage", messageToSend)
        logsChannel = await WaliSetupManager(ctx.guild).get_or_create_logs_channel
        await logsChannel.send(f"```{ctx.user.name} {language['log_command_access_no']} : wal_i```")

mod_manager = ModCommandsManager(tree)


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    await tree.sync()
    for guild in client.guilds:
        wali_channel = await WaliSetupManager(guild).get_or_create_wali_channel()

onMessage(client)
onMessageDelete(client)

client.run(BOT_TOKEN)
