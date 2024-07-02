import discord

from command.loadCommand import load_command
from parameters.fetchSubscribedServers import fetch_servers
from parameters.guildLanguage import guildLanguage
from parameters.logActions import logActions
from parameters.waliSetupManager import WaliSetupManager


import discord
import random
from parameters.guildLanguage import guildLanguage


class ConfirmButton(discord.ui.Button):
    def __init__(self, language):
        super().__init__(style=discord.ButtonStyle.green,
                         label=language['confirm'], custom_id='confirm')

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.value = True
        self.view.stop()


class CancelButton(discord.ui.Button):
    def __init__(self, language):
        super().__init__(style=discord.ButtonStyle.red,
                         label=language['cancel'], custom_id='cancel')

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.value = False
        self.view.stop()


class ConfirmView(discord.ui.View):
    def __init__(self, language):
        super().__init__()
        self.value = None
        self.timeout = 180
        self.add_item(ConfirmButton(language))
        self.add_item(CancelButton(language))


color = (random.randint(0, 255) << 16) | (
    random.randint(0, 255) << 8) | random.randint(0, 255)


class SendMessage:
    def __init__(self, ctx):
        self.ctx = ctx

    async def call_send_message_cmf(self, messageToSend):
        command_func = await load_command("sendMessage")
        await command_func(self.ctx, messageToSend)

    async def log_action(self, log_action):
        await logActions(log_action, self.ctx.guild)


def mod_embed(mod):
    mod_embed = discord.Embed(
        title=f"{mod}",
        description=None,
        color=color
    )
    return mod_embed


def mod_stats_embed(action, limit_value):
    message_delete_embed = discord.Embed(
        title=f"{action}",
        description=None,
        color=color
    ).add_field(name="Limit", value=f"{limit_value}").add_field(name="Used", value="0")
    return message_delete_embed


def mod_records_embed(language):
    mod_records_embed = discord.Embed(
        title=f"{language['mod_records']}",
        description=None,
        color=color
    ).add_field(name="Kicks", value="0").add_field(name="Bans", value="0").add_field(name="Timeouts", value="0").add_field(name="Messages", value="0")
    return mod_records_embed


async def createMod(ctx, mod, kicks, bans, timeouts, messages, language):

    wali_mods_role = await WaliSetupManager(ctx.guild).get_or_create_mod_role()

    messageToSend = None

    mod_found = False
    wali_cannot_mod = False
    guild_owner_cannnot_mod = False

    wali_mods_channel = await WaliSetupManager(ctx.guild).get_or_create_wali_mods_channel()

    async for message in wali_mods_channel.history(limit=None):
        if message.author == ctx.client.user and message.embeds:
            modEmbed = message.embeds[0]
            if modEmbed.title == mod.name:
                mod_found = True

            if ctx.client.user.id == mod.id:
                wali_cannot_mod = True

            if ctx.guild.owner_id == mod.id:
                guild_owner_cannnot_mod = True

    if mod_found:
        if wali_mods_role not in mod.roles:
            view = ConfirmView(language=language)
            confirmation_message = await ctx.followup.send(content=f"```{language['reassign_mod_role_confirmation_message']}```", view=view, ephemeral=True)
            await view.wait()
            if view.value:
                await confirmation_message.delete()
                await WaliSetupManager(ctx.guild).get_or_create_mod_channel()
                await mod.add_roles(wali_mods_role)
                messageToSend = f"{language['mod_role_reassigned']}: {mod} "
                log_action = f"```{language['mod_role_reassigned']} {mod}```"
                await SendMessage(ctx).log_action(log_action)
            if view.value is None:
                await confirmation_message.delete()
                messageToSend = f"{language['confirmation_timeout']}"
        else:
            messageToSend = f"{mod} {language['mod_already_exist']}"

    elif wali_cannot_mod:
        messageToSend = f"{language['wali_cannot_mod']}"

    elif guild_owner_cannnot_mod:
        messageToSend = f"{language['guild_owner_cannot_mod']}"

    else:
        await WaliSetupManager(ctx.guild).get_or_create_mod_channel()
        await mod.add_roles(wali_mods_role)
        await wali_mods_channel.send(embeds=[
            mod_embed(mod),
            mod_records_embed(language),
            mod_stats_embed("Kicks", kicks),
            mod_stats_embed("Bans", bans),
            mod_stats_embed("Timeouts", timeouts),
            mod_stats_embed("Messages", messages)
        ])
        messageToSend = f"{language['mod_created']}: {mod}"
        log_action = f"```{language['mod_created']} \nmod: {mod}```"
        await SendMessage(ctx).log_action(log_action)

    await SendMessage(ctx).call_send_message_cmf(messageToSend)


async def resetModStats(ctx, mod, language, kick: bool = False, ban: bool = False, timeout: bool = False, msg: bool = False):
    wali_mods_channel_name = f'wal-i-mods'
    wali_mods_channel = discord.utils.get(
        ctx.guild.text_channels, name=wali_mods_channel_name)
    messageToSend = None
    mod_found = False

    if wali_mods_channel is not None:
        async for message in wali_mods_channel.history(limit=None):
            if message.author == ctx.client.user and message.embeds:
                modEmbed = message.embeds[0]
                if modEmbed.title == mod.name:
                    mod_found = True
                    embed_titles = {
                        embed.title: embed for embed in message.embeds}
                    actions = {
                        "Kicks": kick,
                        "Bans": ban,
                        "Timeouts": timeout,
                        "Messages": msg
                    }

                    updated_embeds = []
                    messages = []

                    for title, action in actions.items():
                        if action:
                            if title in embed_titles:
                                embed = embed_titles[title].copy()
                                embed.set_field_at(
                                    1, name=embed.fields[1].name, value="0")
                                updated_embeds.append(embed)
                            else:
                                messages.append(
                                    f"The mod cannot {title.lower()}.")

                    if updated_embeds:
                        await message.edit(embeds=updated_embeds)
                        messageToSend = f"Mod {mod} {'kicks' if kick else ''} {'bans' if ban else ''} {'timeouts' if timeout else ''} {'messages' if msg else ''} {language['log_mod_reset']}"
                        log_action = f"```Mod {mod} {'kicks' if kick else ''} {'bans' if ban else ''} {'timeouts' if timeout else ''} {'messages' if msg else ''} {language['log_mod_reset']} ```"
                        await SendMessage(ctx).log_action(log_action)
                    if messages:
                        messageToSend = "\n".join(messages)
        if not mod_found:
            messageToSend = f"{mod} {language['no_mod_found']}"

    else:
        messageToSend = f"{language['no_mod_yet']}"

    await SendMessage(ctx).call_send_message_cmf(messageToSend)


async def editModStats(ctx, mod, kicks, bans, timeouts, msgs, language):
    wali_mods_channel_name = f'wal-i-mods'
    wali_mods_channel = discord.utils.get(
        ctx.guild.text_channels, name=wali_mods_channel_name)
    messageToSend = None
    mod_found = False

    if wali_mods_channel is not None:
        async for message in wali_mods_channel.history(limit=None):
            if message.author == ctx.client.user and message.embeds:
                modEmbed = message.embeds[0]
                if modEmbed.title == mod.name:
                    mod_found = True
                    embed_titles = {
                        embed.title: embed for embed in message.embeds}
                    values = {
                        "Kicks": kicks,
                        "Bans": bans,
                        "Timeouts": timeouts,
                        "Messages": msgs
                    }

                    updated_embeds = []

                    for title, value in values.items():
                        if value > 0:
                            if title in embed_titles:
                                embed = embed_titles[title].copy()
                                embed.set_field_at(
                                    0, name=embed.fields[0].name, value=f"{value}")
                            else:
                                embed = discord.Embed(title=title)
                                embed.add_field(name="Count", value=f"{value}")
                            updated_embeds.append(embed)
                        elif title in embed_titles:
                            updated_embeds.append(embed_titles[title])

                    await message.edit(embeds=updated_embeds)
                    messageToSend = f"Mod {mod} {'kicks' if kicks > 0 else ''} {'bans' if bans > 0 else ''} {'timeouts' if timeouts > 0 else ''} {'messages' if msgs > 0 else ''} limit {language['log_mod_limit_change']}"
                    log_action = f"```Mod {mod} {'kicks' if kicks > 0 else ''} {'bans' if bans > 0 else ''} {'timeouts' if timeouts > 0 else ''} {'messages' if msgs > 0 else ''} limit {language['log_mod_limit_change']}```"
                    await SendMessage(ctx).log_action(log_action)
        if not mod_found:
            messageToSend = f"{mod} {language['no_mod_found']}"

    else:
        messageToSend = f"{language['no_mod_yet']}"

    await SendMessage(ctx).call_send_message_cmf(messageToSend)

mod_channel_name = f"wal-i-mods-channel"
wali_channel_name = 'wal-i'


async def handle_reset_command(ctx, mod, kick, ban, timeout, message):

    servers = fetch_servers()

    language = guildLanguage(ctx.guild)

    if ctx.guild.id not in servers:
        await ctx.response.send_message(f"```{language['no_active_subscription']}```", ephemeral=True)
        return

    if ctx.channel.name != 'wal-i-mods-channel' and ctx.channel.name != 'wal-i':
        await ctx.response.defer(ephemeral=True)
    else:
        await ctx.response.defer()

    if ctx.user.id == ctx.guild.owner_id:
        await resetModStats(ctx, mod, language, kick, ban, timeout, message)
    else:
        messageToSend = f"{language['command_access_no']}"
        log_action = f"```{ctx.user.name} {language['log_command_access_no']} : wal_i_reset_mod```"
        await SendMessage(ctx).call_send_message_cmf(messageToSend)
        await SendMessage(ctx).log_action(log_action)


async def handle_mod_command(ctx, mod, kicks, bans, timeouts, messages, action):

    servers = fetch_servers()

    language = guildLanguage(ctx.guild)

    if ctx.guild.id not in servers:
        await ctx.response.send_message(f"```{language['no_active_subscription']}```", ephemeral=True)
        return

    if ctx.channel.name != 'wal-i-mods-channel' and ctx.channel.name != 'wal-i':
        await ctx.response.defer(ephemeral=True)
    else:
        await ctx.response.defer()

    if ctx.user.id == ctx.guild.owner_id:
        await action(ctx, mod, kicks, bans, timeouts, messages, language)
    else:
        messageToSend = f"{language['command_access_no']}"
        log_action = f"```{ctx.user.name} {language['log_command_access_no']} : {action.__name__}```"
        await SendMessage(ctx).call_send_message_cmf(messageToSend)
        await SendMessage(ctx).log_action(log_action)


class ModCommandsManager:
    def __init__(self, tree):
        self.tree = tree
        self.setup_commands()

    def setup_commands(self):
        @self.tree.command(description="Create Mod")
        async def wal_i_mod(ctx, mod: discord.Member, kicks: int = 10, bans: int = 10, timeouts: int = 10, messages: int = 10):
            await handle_mod_command(ctx, mod, kicks, bans, timeouts, messages, createMod)

        @self.tree.command(description="Edit Mod Stats")
        async def wal_i_edit_mod(ctx, mod: discord.Member, kicks: int = 0, bans: int = 0, timeouts: int = 0, messages: int = 0):
            await handle_mod_command(ctx, mod, kicks, bans, timeouts, messages, editModStats)

        @self.tree.command(description="Reset Mod Stats")
        async def wal_i_reset_mod(ctx, mod: discord.Member, kick: bool = False, ban: bool = False, timeout: bool = False, message: bool = False):
            await handle_reset_command(ctx, mod, kick, ban, timeout, message)


class CheckUpdateModStats:
    def __init__(self, ctx):
        self.ctx = ctx

    async def checkModStats(self, value):
        wali_mods_channel = discord.utils.get(
            self.ctx.guild.text_channels, name='wal-i-mods')
        mod_can_action = False

        language = guildLanguage(self.ctx.guild)

        if wali_mods_channel is not None:
            async for message in wali_mods_channel.history(limit=None):
                if message.author == self.ctx.client.user and message.embeds:
                    updated_embeds = []
                    modEmbed = message.embeds[0]

                    if modEmbed.title == self.ctx.user.name:
                        for embed in message.embeds:
                            updated_embed = embed.copy()
                            if embed.title == value:
                                if int(embed.fields[0].value) > int(embed.fields[1].value):
                                    mod_can_action = True
                                    updated_embed.set_field_at(
                                        1, name=embed.fields[1].name, value=str(int(embed.fields[1].value) + 1))
                                else:
                                    await SendMessage(self.ctx).log_action(f"```{self.ctx.user.name} {language['mod_tried_limit_reached']} {value}```")
                                    await SendMessage(self.ctx).call_send_message_cmf(f"```{language['mod_limit_reached']} {value}```")

                            updated_embeds.append(updated_embed)

                        if mod_can_action:
                            for embed in updated_embeds:
                                if embed.title == language['mod_records']:
                                    for field in embed.fields:
                                        if field.name == value:
                                            index = embed.fields.index(field)
                                            embed.set_field_at(
                                                index, name=field.name, value=str(int(field.value) + 1))

                        await message.edit(embeds=updated_embeds)
                        break
        return mod_can_action

    async def modKick(self):
        mod_can_kick = await self.checkModStats("Kicks")
        return mod_can_kick

    async def modBan(self):
        mod_can_ban = await self.checkModStats("Bans")
        return mod_can_ban

    async def modTimeout(self):
        mod_can_timeout = await self.checkModStats("Timeouts")
        return mod_can_timeout

    async def modMessage(self):
        mod_can_delete_message = await self.checkModStats("Messages")
        return mod_can_delete_message
