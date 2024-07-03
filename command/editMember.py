import re
import json
import discord

from command.loadCommand import load_command
from parameters.guildLanguage import guildLanguage


async def editMember(ctx, command):

    delete_message_seconds = None
    until = None
    reason = None
    miscellaneous_match = None
    members = []
    role_names = []

    responses = []

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
                delete_message_seconds = 86, 400
            elif delete_duration == "Previous 3 Days":
                delete_message_seconds = 259, 200
            elif delete_duration == "Previous 7 Days":
                delete_message_seconds = 604, 800

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
                        f"```{language['no_member']} : {member_name}```")
                    continue
                else:
                    members.append(member)

        if matches_dict["reason"]:
            reason = matches_dict["reason"][1].strip(" ").strip('"')

        if members:
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
                        if matches_dict["deleteMessage"]:
                            await member.ban(delete_message_seconds=delete_message_seconds, reason=reason)
                        else:
                            await member.ban(reason=reason)

                        responses.append(
                            f"```{member.name} {language['was_banned']}```")
                    
                    if matches_dict["kick"]:
                        await member.kick(reason=reason)
                        responses.append(
                            f"```{member.name} {language['was_kicked']}```")
                  
                    if matches_dict["timeout"]:
                        if matches_dict["duration"]:
                            await member.timout(until=until, reason=reason)
                        else:
                            await member.timeout(reason=reason)
                        responses.append(
                            f"```{member.name} {language['was_timed_out']} {duration}```")
                  
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
                                    f"```{language['no_role_found']} : {role_name}```")
                                return
                            await member.add_roles(role)
                            responses.append(
                                f"```{member.name} {language['was_given_role']} {role.name}```")
                         
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
                                    f"```{language['no_role_found']} : {role_name}```")
                                return
                            await member.remove_roles(role)
                            responses.append(
                                f"```{member.name} {language['was_removed_role']} {role.name}```")
                
                except Exception as e:
                    print(e)
                    responses.append(
                        f"```{language['no_enough_permission']} {member.name}```")

    else:
        responses.append(
            f"```{language['invalid']}```")

    messageToSend = responses
    command_name = "sendMessage"
    command_func = await load_command(command_name)
    await command_func(ctx, messageToSend)
