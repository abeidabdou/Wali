import discord
import os
from ai_studio_api_call import generate_instructions
import re
from events.onDeleteMessage import onMessageDelete
from events.onInteractionErrors import onInteractionErrors
from events.onMessage import onMessage
from modules.modManager import ModCommandsManager
from parameters.fetchSubscribedServers import fetch_servers
from parameters.guildLanguage import guildLanguage
from parameters.waliSetupManager import WaliSetupManager
from discord import app_commands
from dotenv import load_dotenv
from command.loadCommand import load_command
from redis.asyncio import Redis

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

EXPIRATION_TIME = 300


async def callCommand(ctx, command_name, command_args):
    command_func = await load_command(command_name)
    await command_func(ctx, command_args)


@tree.command(description="Invoke Wali")
async def wal_i(ctx, request: str):

    message = request

    language = guildLanguage(ctx.guild)
    servers = fetch_servers()

    if ctx.guild.id not in servers:
        await ctx.response.send_message(f"```{language['no_active_subscription']}```", ephemeral=True)
        return

    wali_mods_role_name = 'wal-i-mod'

    user_id = str(ctx.user.id)
    guild_id = str(ctx.guild.id)

    if ctx.user.id == ctx.guild.owner_id or wali_mods_role_name in [role.name for role in ctx.user.roles]:
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


@tree.command(description="Setup Wali")
async def wal_i_setup(ctx):

    language = guildLanguage(ctx.guild)
    servers = fetch_servers()

    if ctx.guild.id not in servers:
        await ctx.response.send_message(f"```{language['no_active_subscription']}```", ephemeral=True)
        return

    if ctx.user.id == ctx.guild.owner_id:
        if ctx.channel.name != 'wal-i-mods-channel' and ctx.channel.name != 'wal-i':
            await ctx.response.send_message(f"```{language['wali_setup_message']}```", ephemeral=True)
        else:
            await ctx.response.send_message(f"```{language['wali_setup_message']}```")

        await WaliSetupManager(ctx.guild).get_or_create_wali_channel()


async def store_user_data(user_id, guild_id, data_type, data):
    key = f"user:{user_id}:{guild_id}"

    await redis.rpush(key, f"{data_type}: {data}")
    await redis.expire(key, EXPIRATION_TIME)


async def get_previous_interactions(user_id, guild_id):
    key = f"user:{user_id}:{guild_id}"
    interactions = await redis.lrange(key, 0, -1)
    formatted_interactions = "\n".join(interactions)
    return formatted_interactions


async def initialize_redis():
    global redis
    redis = Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        password=os.getenv('REDIS_PASSWORD'),
        encoding='utf-8',
        decode_responses=True
    )

mod_manager = ModCommandsManager(tree)


@client.event
async def on_ready():
    servers = fetch_servers()
    await initialize_redis()
    await tree.sync()
    for guild in client.guilds:
        wali_channel = await WaliSetupManager(guild).get_or_create_wali_channel()


onMessage(client)
onMessageDelete(client)
onInteractionErrors(client)

client.run(BOT_TOKEN)
