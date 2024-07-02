import discord
import re
import json
from command.loadCommand import load_command
from datetime import datetime
import pytz
import asyncio
import validators

from modules.modManager import CheckUpdateModStats
from parameters.guildLanguage import guildLanguage
from parameters.logActions import logActions


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


async def fetch_message_in_channels(ctx, message_id):
    for channel in ctx.guild.channels:
        if channel.type not in (discord.ChannelType.forum, discord.ChannelType.category):
            try:
                msg = await channel.fetch_message(message_id)
                if msg:
                    return msg
            except discord.NotFound:
                continue
    return None


def contains_link(text):
    words = text.split()
    for word in words:
        if validators.url(word):
            return True
    return False


async def parse_custom_datetime(custom_str):
    if custom_str.startswith('year.now-month.now-day.now'):
        time_part = custom_str.split(' ')[1]
        hours, minutes, seconds = map(int, time_part.split(':'))
        now = datetime.now(pytz.utc)
        custom_datetime = now.replace(
            hour=hours, minute=minutes, second=seconds, microsecond=0)
        return custom_datetime
    return None


def logEmbed(ctxUser, value, reason, language):
    log_embed = discord.Embed(
        title=f"{language['log_message_deleted']} {language['by']} {ctxUser}",
        description=value,
        color=0xD48C70
    ).add_field(name=language['reason_label'], value=reason)
    return log_embed

def extract_embed_content(message):
    embed_contents = []
    for embed in message.embeds:
        parts = []
        if embed.title:
            parts.append(f"Title: {embed.title}")
        if embed.description:
            parts.append(f"Description: {embed.description}")
        for field in embed.fields:
            parts.append(f"{field.name}: {field.value}")
        if embed.footer:
            parts.append(f"Footer: {embed.footer.text}")
        embed_contents.append('\n'.join(parts))
    return '\n---\n'.join(embed_contents)

async def deleteMessage(ctx, command):

    language = guildLanguage(ctx.guild)

    wali_mods_role_name = 'wal-i-mod'

    messageToSend = None
    before = None
    after = None
    contains = None
    before_after = None
    miscellaneous_match = None
    reason = None
    attachement = None
    contains = None
    responses = []
    channels = []
    messages = []
    users = []
    logsEmbed = []
    logs = []
    mod_tried_delete_by_date = False
    messages_deleted = 0

    matchs = re.findall(r'(\w+)[\[\(](.*?)[\]\)]', command)

    matches_dict = {
        "channel": None,
        "member": None,
        "before": None,
        "after": None,
        "message_contains": None,
        "attachement": None,
        "limit": None,
        "deleteMessage": None,
        "reason": None,
    }

    for match in matchs:
        match_type = match[0]
        if match_type in matches_dict:
            matches_dict[match_type] = match
        else:
            miscellaneous_match = match

    if matches_dict["channel"]:
        channel_spec = matches_dict["channel"][1]
        if channel_spec == "0":
            if ctx.user.id != ctx.guild.owner_id:
                responses.append(f"{language['delete_message_no_permission']}")
                logs.append(
                    f"```{ctx.user.name} {language['log_delete_message_no_permission']}```")
                return
            channels = [
                channel for channel in ctx.guild.channels]
        elif channel_spec == "1":
            channels.append(ctx.channel)
        else:
            channel_names = channel_spec.split(',')
            for name in channel_names:
                name = name.strip(" ").strip('"')
                channel = ctx.guild.get_channel(int(name)) if name.isdigit(
                ) else discord.utils.get(ctx.guild.channels, name=name.lower())
                if channel:
                    channels.append(channel)
                else:
                    responses.append(f"{language['no_channel_found']}: {name}")

    if matches_dict["member"]:
        urs = matches_dict["member"][1].split(',')
        for user in urs:
            user = user.strip(" ").strip('"')
            member = ctx.guild.get_member(int(user)) if user.isdigit(
            ) else discord.utils.get(ctx.guild.members, name=user.lower())
            if user == '1':
                users.append(ctx.user)
            elif member:
                users.append(member)
            else:
                responses.append(
                    f"{language['no_member']}: {user}")

    if users:
        remaining_users = []
        for user in users:
            if ctx.user.id != ctx.guild.owner_id and (user.id == ctx.guild.owner_id or user.guild_permissions.administrator or wali_mods_role_name in [role.name for role in user.roles]):
                responses.append(
                    f"{language['delete_message_user_no_permission']} : {user.name}")
                logs.append(
                    f"```{ctx.user.name} {language['log_delete_message_user_no_permission']} : {user.name}```")
            else:
                remaining_users.append(user)

        users = remaining_users

    channel_before = None
    channel_after = None

    if matches_dict["before"]:
        before = matches_dict["before"][1]
        if not before.isdigit():
            if ctx.user.id == ctx.guild.owner_id:
                before_datetime = parse_custom_datetime(before)
                if before_datetime is None:
                    before_datetime = pytz.utc.localize(
                        datetime.strptime(before, '%Y-%m-%d %H:%M:%S'))
                before = before_datetime
            else:
                mod_tried_delete_by_date = True
                before = None
                channels = []
        else:
            result = await fetch_message_in_channels(ctx, before)
            if result:
                channel_before = result.channel
            else:
                responses.append(f"{language['message_not_found']}: {before}")
                before = None

    if matches_dict["after"]:
        after = matches_dict["after"][1]
        if not after.isdigit():
            if ctx.user.id == ctx.guild.owner_id:
                after_datetime = parse_custom_datetime(after)
                if after_datetime is None:
                    after_datetime = pytz.utc.localize(
                        datetime.strptime(after, '%Y-%m-%d %H:%M:%S'))
                after = after_datetime
            else:
                mod_tried_delete_by_date = True
                after = None
                channels = []
        else:
            result = await fetch_message_in_channels(ctx, after)
            if result:
                channel_after = result.channel
            else:
                responses.append(f"{language['message_not_found']}: {after}")
                after = None

    if mod_tried_delete_by_date:
        responses.append(
            f"{language['mod_can_not_delete_by_date']}")
        logs.append(
            f"```{ctx.user.name} {language['log_mod_can_not_delete_by_date']}```")

    before_after = before and after

    if before_after and channel_before and channel_after:
        if channel_before != channel_after:
            channels = []
            responses.append(f"{language['before_after_different_channel']}")
        else:
            channels = [channel_before]

    elif channel_before:
        channels = [channel_before]

    elif channel_after:
        channels = [channel_after]

    if matches_dict["message_contains"]:
        contains = matches_dict["message_contains"][1].split(',')
        contains = [word.strip(" ").strip('"') for word in contains]

    if matches_dict["attachement"]:
        attachement = matches_dict["attachement"][1].split(',')
        attachement = [word.strip(" ").strip('"') for word in attachement]

    limit = matches_dict["limit"][1] if matches_dict["limit"] else None

    if matches_dict["reason"]:
        reason = matches_dict["reason"][1].strip(" ").strip('"')

    if channels:
        filtered_channels = []
        for channel in channels:
            if isinstance(channel, discord.CategoryChannel) or isinstance(channel, discord.ForumChannel) or isinstance(channel, discord.VoiceChannel):
                responses.append(
                    f"{language['delete_message_category_and_forum_no']}: {channel.name} {language['is']} {channel.type}")
            elif ctx.user not in channel.members or ("wal-i" in channel.name and ctx.user.id != ctx.guild.owner_id):
                responses.append(
                    f"{language['delete_message_no_permission_channel']} : {channel.name}")
                logs.append(
                    f"```{ctx.user.name} {language['log_delete_message_in_channel_no_permission']} : {channel.name}```")
            else:
                filtered_channels.append(channel)
        channels = filtered_channels

    if limit:
        if limit.isdigit():
            limit = int(limit)
        elif limit == "None" and ctx.user.id == ctx.guild.owner_id:
            limit = None
        else:
            responses.append(f"{language['specify_limit']}")
            channels = []

    if channels:
        for channel in channels:

            async for message in channel.history(limit=None):
                if limit and len(messages) >= limit and before_after is False:
                    break

                if before_after:
                    if isinstance(before, datetime) and isinstance(after, datetime):
                        if not (after < message.created_at < before):
                            continue
                    else:
                        if not (int(after) < message.id < int(before)):
                            continue
                elif before and (isinstance(before, datetime) and message.created_at >= before or message.id >= int(before)):
                    continue
                elif after and (isinstance(after, datetime) and message.created_at <= after or message.id <= int(after)):
                    continue

                if contains:
                    if not any(word in message.content for word in contains):
                        continue

                if attachement:
                    attachement_found = False
                    for word in attachement:
                        if word == "link":
                            if contains_link(message.content):
                                attachement_found = True
                                break
                        else:
                            if any(word in attachment.content_type for attachment in message.attachments):
                                attachement_found = True
                                break

                    if attachement_found is False:
                        continue

                if matches_dict["member"]:
                    if users and message.author not in users:
                        continue
                    if not users:
                        break

                messages.append(message)

    if matches_dict["deleteMessage"]:
        msgs = [int(id) for id in matches_dict["deleteMessage"][1].split(',')]
        for message in msgs:
            result = await fetch_message_in_channels(ctx, message)
            if result:
                messages.append(result)
            else:
                responses.append(
                    f"{language['message_not_found']} : {message}")

    if not messages:
        responses.append(f"{language['no_message_found']}")

    view = None
    if messages:
        view = ConfirmView(language=language)
        conditional_message_part = f"{language['about_to_delete']} {len(messages)} messages\n" if len(
            messages) > 1 else f"{language['about_to_delete']} {len(messages)} message\n"
        confirmation_message = await ctx.followup.send(content=f"```{conditional_message_part} {language['confirmation_message']}```", view=view, ephemeral=True)
        await view.wait()

    if view and view.value and not miscellaneous_match:
        await confirmation_message.delete()
        for message in messages:
            mod_can_delete_messages = await CheckUpdateModStats(ctx).modMessage()
            if isinstance(message, discord.Message) and (ctx.user.id == ctx.guild.owner_id or mod_can_delete_messages):
                try:
                    if message.channel.type not in (discord.ChannelType.private_thread, discord.ChannelType.public_thread):
                        for thread in message.channel.threads:
                            if message.id == thread.id:
                                await thread.delete()
                    embed_content = extract_embed_content(message)
                    combined_content = message.content + "\nEmbeds:\n" + embed_content if message.content and embed_content else message.content or embed_content
                    await message.delete()
                    responses.append(
                        f"```{language['message_deleted']} : {message.id}\n{language['channel']} : {message.channel.name}```")
                    logsEmbed.append(logEmbed(ctx.user.name, combined_content, reason, language))
                    await asyncio.sleep(0.09)
                except discord.Forbidden:
                    responses.append(
                        f"{language['delete_message_invalid_permission']} : {message.id} {language['channel']} : {message.channel.name}, {language['message_system']}")

    messageToSend = responses

    if view and view.value is None:
        await confirmation_message.delete()
        messageToSend = f"{language['confirmation_none']}"

    if view and view.value is False:
        messageToSend = f"{language['confirmation_delete_no']}, {language['deleted_none']}"
        await confirmation_message.delete()

    if miscellaneous_match:
        messageToSend = f"{language['delete_message_invalid_parameter']} : {miscellaneous_match[0]}"

    if logs:
        log_action = logs
        await logActions(log_action, ctx.guild)

    if logsEmbed:
        await logActions(logsEmbed, ctx.guild)

    command_name = "sendMessage"
    command_func = await load_command(command_name)
    await command_func(ctx, messageToSend)
