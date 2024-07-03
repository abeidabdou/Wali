import discord
import os
from ai_studio_api_call import generate_instructions
import re
from context import get_previous_interactions, initialize_redis, store_user_data
from events.onMessage import onMessage
from parameters.guildLanguage import guildLanguage
from parameters.waliSetupManager import WaliSetupManager
from discord import app_commands
from dotenv import load_dotenv
from command.loadCommand import load_command

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


async def callCommand(ctx, command_name, command_args):
    command_func = await load_command(command_name)
    await command_func(ctx, command_args)


@tree.command(description="Invoke Wali")
async def wal_i(ctx, request: str):

    try:

        message = request

        language = guildLanguage(ctx.guild)

        user_id = str(ctx.user.id)
        guild_id = str(ctx.guild.id)

        if ctx.user.id == ctx.guild.owner_id:
            if ctx.channel.name != 'wal-i-mods-channel' and ctx.channel.name != 'wal-i':
                await ctx.response.send_message(f"```{message}```", ephemeral=True)
            else:
                await ctx.response.send_message(f"```{message}```")

            previous_interactions = await get_previous_interactions(user_id, guild_id)

            await store_user_data(user_id, guild_id, "input", message)

            prompt = f"{previous_interactions}\ninput: {message}"

            response = await generate_instructions(prompt)

            response_text = response.text

            match = re.match(r'(\w+)', response_text)
            if match:
                command_name = match.group(1)
                await callCommand(ctx, command_name, response_text)

            await store_user_data(user_id, guild_id, "output", response_text)
        else:
            await ctx.response.defer(ephemeral=True)
            messageToSend = f"```{language['command_access_no']}```"
            await callCommand(ctx, "sendMessage", messageToSend)
            logsChannel = await WaliSetupManager(ctx.guild).get_or_create_logs_channel
            await logsChannel.send(f"```{ctx.user.name} {language['log_command_access_no']} : wal_i```")

    except Exception as e:
        print(e)


@tree.command(description="Setup Wali")
async def wal_i_setup(ctx):

    try:

        language = guildLanguage(ctx.guild)

        if ctx.user.id == ctx.guild.owner_id:
            if ctx.channel.name != 'wal-i-mods-channel' and ctx.channel.name != 'wal-i':
                await ctx.response.send_message(f"```{language['wali_setup_message']}```", ephemeral=True)
            else:
                await ctx.response.send_message(f"```{language['wali_setup_message']}```")

            await WaliSetupManager(ctx.guild).get_or_create_wali_channel()

    except Exception as e:
        print(e)


@client.event
async def on_ready():
    await initialize_redis()
    await tree.sync()
    for guild in client.guilds:
        wali_channel = await WaliSetupManager(guild).get_or_create_wali_channel()

onMessage(client)

client.run(BOT_TOKEN)
