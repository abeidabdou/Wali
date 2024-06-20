import re
import json
import discord

from command.loadCommand import load_command
from modules.modManager import CheckUpdateModStats
from parameters.guildLanguage import guildLanguage
from parameters.waliSetupManager import WaliSetupManager


async def editMember(ctx, command):

    delete_message_seconds = None
    until = None
    delete_message_days = None
    miscellaneous_match = None
    members = []
    role_names = []

    responses = []

    logs = []

    logsChannel = await WaliSetupManager(ctx.guild).get_or_create_logs_channel()

    language = guildLanguage(ctx.guild)

    matchs = re.findall(r'(\w+)(?:[\[\(](.*?)[\]\)])?', command)

    matches_dict = {
        "editMember": None,
        "removeRole": None,
        "addRole": None,
        "duration": None,
        "deleteMessage": None,
        "reason": None,
        "ban": None,
        "kick": None,
        "timeout": None,
        "mute": None,
        "unmute": None,
        "muteSoundBoard": None,
        "unmuteSoundBoard": None
    }

    for match in matchs:
        match_type = match[0]
        if match_type in matches_dict:
            matches_dict[match_type] = match
        else:
            miscellaneous_match = match

    if not miscellaneous_match:

        if matches_dict["deleteMessage"]:
            delete_duration = matches_dict["deleteMessage"][1].strip(
                " ").strip('"')
            if delete_duration == "Previous Hour":
                delete_message_seconds = 3600
            elif delete_duration == "Previous 6 Hours":
                delete_message_seconds = 21600
            elif delete_duration == "Previous 12 Hours":
                delete_message_seconds = 43200
            elif delete_duration == "Previous 24 Hours":
                delete_message_days = 1
            elif delete_duration == "Previous 3 Days":
                delete_message_days = 3
            elif delete_duration == "Previous 7 Days":
                delete_message_days = 7

        if matches_dict["duration"]:
            duration = matches_dict["duration"][1].strip(" ").strip('"')
            if duration == "60 SECS":
                until = 60
            elif duration == "5 MINS":
                until = 300
            elif duration == "10 MINS":
                until = 600
            elif duration == "1 HOUR":
                until = 3600
            elif duration == "1 DAY":
                until = 86400
            elif duration == "1 WEEK":
                until = 604800

        if matches_dict["editMember"]:
            matched_names = matches_dict["editMember"][1]
            member_names = matched_names.split(',')
            member_names = [name.strip(" ").strip('"')
                            for name in member_names]
            for member_name in member_names:
                member = ctx.guild.get_member(int(member_name)) if member_name.isdigit(
                ) else discord.utils.get(ctx.guild.members, name=member_name.lower())
                if not member:
                    responses.append(
                        f"{language['no_member']} : {member_name}")
                    return
                else:
                    members.append(member)

        for member in members:
            try:
                if member.voice:
                    if matches_dict["mute"]:
                        await member.edit(mute=True)

                    if matches_dict["unmute"]:
                        await member.edit(mute=False)

                    if matches_dict["muteSoundBoard"]:
                        for member in members:
                            await member.edit(deafen=True)

                    if matches_dict["unmuteSoundBoard"]:
                        await member.edit(deafen=False)

                if matches_dict["ban"]:
                    mod_can_ban = await CheckUpdateModStats(ctx).modBan()
                    if ctx.user.id == ctx.guild.owner_id or mod_can_ban:
                        if matches_dict["deleteMessage"]:
                            await member.ban(delete_message_days=delete_message_days, delete_message_seconds=delete_message_seconds, reason=matches_dict["reason"][1].strip(" ").strip('"'))
                        else:
                            await member.ban(reason=matches_dict["reason"][1].strip(" ").strip('"'))

                        responses.append(
                            f"{member.name} {language['was_banned']}")
                        logs.append(f"{ctx.user.name} {language['banned']} {member.name}\n\n {language['reason']} {matches_dict['reason'][1].strip(' ').strip('\"')}")

                if matches_dict["kick"]:
                    mod_can_kick = await CheckUpdateModStats(ctx).modKick()
                    if ctx.user.id == ctx.guild.owner_id or mod_can_kick:
                        await member.kick(reason=matches_dict["reason"][1].strip(" ").strip('"'))
                        responses.append(
                            f"{member.name} {language['was_kicked']}")
                        logs.append(f"{ctx.user.name} {language['kicked']} {member.name}\n\n {language['reason']} {matches_dict['reason'][1].strip(' ').strip('\"')}")

                if matches_dict["timeout"]:
                    mod_can_timeout = await CheckUpdateModStats(ctx).modTimeout()
                    if ctx.user.id == ctx.guild.owner_id or mod_can_timeout:
                        if matches_dict["duration"]:
                            await member.timout(until=until, reason=matches_dict["reason"][1].strip(" ").strip('"'))
                        else:
                            await member.timeout(reason=matches_dict["reason"][1].strip(" ").strip('"'))
                        responses.append(
                            f"{member.name} {language['was_timed_out']} {duration}")
                        logs.append(f"{ctx.user.name} {language['timed_out']} {member.name} {language['for']} {duration}\n\n {language['reason']} {matches_dict['reason'][1].strip(' ').strip('\"')}")
            except:
                responses.append(
                    f"{language['no_permission']} {'mute' if matches_dict['mute'] else ''} {'unmute' if matches_dict['unmute'] else ''} {'ban' if matches_dict['ban'] else ''} {'kick' if matches_dict['kick'] else ''} {'timeout' if matches_dict['timeout'] else ''} {member.name}")
                logs.append(f"{ctx.user.name} {language['no_permission_tried']} {'mute' if matches_dict['mute'] else ''} {'unmute' if matches_dict['unmute'] else ''} {'ban' if matches_dict['ban'] else ''} {'kick' if matches_dict['kick'] else ''} {'timeout' if matches_dict['timeout'] else ''} {member.name}")

            if ctx.user.id == ctx.guild.owner_id:

                try:

                    if matches_dict["addRole"]:
                        role_names_to_add = matches_dict["addRole"][1]
                        role_names = role_names_to_add.split(',')
                        role_names = [name.strip(" ").strip('"')
                                      for name in role_names]
                        for role_name in role_names:
                            role = discord.utils.get(ctx.guild.roles, name=role_name.lower()) if not role_name.isdigit(
                            ) else discord.utils.get(ctx.guild.roles, id=int(role_name))
                            if not role:
                                responses.append(
                                    f"{language['no_role_found']} : {role_name}")
                                return
                            await member.add_roles(role)
                            responses.append(
                                f"{member.name} {language['was_given_role']} {role.name}")
                            logs.append(
                                f"{member.name} {language['was_given_role']} {role.name}")

                    if matches_dict["removeRole"]:
                        role_names_to_removeRole = matches_dict["removeRole"][1]
                        role_names = role_names_to_removeRole.split(',')
                        role_names = [name.strip(" ").strip('"')
                                      for name in role_names]
                        for role_name in role_names:
                            role = discord.utils.get(ctx.guild.roles, name=role_name.lower()) if not role_name.isdigit(
                            ) else discord.utils.get(ctx.guild.roles, id=int(role_name))
                            if not role:
                                responses.append(
                                    f"{language['no_role_found']} : {role_name}")
                                return
                            await member.remove_roles(role)
                            responses.append(
                                f"{member.name} {language['was_removed_role']} {role.name}")
                            logs.append(
                                f"{member.name} {language['was_removed_role']} {role.name}")
                except:
                    responses.append(
                        f"{language['no_enough_permission']} {member.name}")

        log_action = f"```{json.dumps(logs)}```"
        await logsChannel.send(log_action)

    else:
        responses.append(
            f"{language['invalid']} : {miscellaneous_match[0]}\n{language['try_again']}")

    messageToSend = '\n'.join(responses)
    command_name = "sendMessage"
    command_func = await load_command(command_name)
    await command_func(ctx, messageToSend)
