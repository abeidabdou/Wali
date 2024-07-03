import discord
from command.loadCommand import load_command
import re
import json
from parameters.guildLanguage import guildLanguage


async def updateChannel(ctx, command):

    responses = []

    guild = ctx.guild
    language = guildLanguage(guild)

    channels = []
    roles = []
    add_permissions = []
    remove_permissions = []
    miscellaneous_match = None

    matchs = re.findall(r'(\w+)[\[\(](.*?)[\]\)]', command)

    matches_dict = {
        "updateChannel": None,
        "role": None,
        "addPermissons": None,
        "removePermissons": None
    }

    for match in matchs:
        match_type = match[0]
        if match_type in matches_dict:
            matches_dict[match_type] = match
        else:
            miscellaneous_match = match

    if matches_dict["updateChannel"]:
        matched_names = matches_dict["updateChannel"][1]
        channel_names = matched_names.split(',')
        channel_names = [name.strip(" ").strip('"') for name in channel_names]
        for chan in channel_names:
            channel = None
            if chan.isdigit():
                channel = guild.get_channel(int(chan))
                channels.append(channel)
            elif not chan.isdigit():
                channel = discord.utils.get(guild.channels, name=chan.lower())
                channels.append(channel)

            if channel == None:
                responses.append(f"```{language['no_channel_found']} : {chan}```")

    if matches_dict["role"]:
        role_names = matches_dict["role"][1]
        role_names = role_names.split(',')
        role_names = [name.strip(" ").strip('"')
                      for name in role_names]
        for role_name in role_names:

            if role_name == "everyone":
                role_name = "@everyone"

            if role_name.isdigit():
                role = discord.utils.get(guild.roles, id=int(role_name))
                if role:
                    roles.append(role)
                else:
                    responses.append(
                        f"```{language['no_role_found']} : {role_name}```")
            else:
                role = discord.utils.get(guild.roles, name=role_name.lower())
                if role:
                    roles.append(role)
                else:
                    responses.append(
                        f"```{language['no_role_found']} : {role_name}```")

    if matches_dict["addPermissons"]:
        add_permissions = matches_dict["addPermissons"][1]
        add_permissions = add_permissions.split(',')
        add_permissions = [perm.strip(" ").strip('"')
                           for perm in add_permissions]

    if matches_dict["removePermissons"]:
        remove_permissions = matches_dict["removePermissons"][1]
        remove_permissions = remove_permissions.split(',')
        remove_permissions = [perm.strip(" ").strip(
            '"') for perm in remove_permissions]

    if not miscellaneous_match:
        for channel in channels:
            if not roles:
                break

            if not channel:
                break

            for target in roles:
                overwrites = channel.overwrites_for(target)

                for perm in add_permissions:
                    try:
                        setattr(overwrites, perm, True)
                        await channel.set_permissions(target, overwrite=overwrites)
                        responses.append(
                            f"```{language['permissions_updated']} : {perm}, {channel.name} {language['for']} {target.name}```")
                    except:
                        responses.append(
                            f"```{language['invalid_permissions']} : {perm}, {channel.name} {language['for']} {target.name}```")
                for perm in remove_permissions:
                    try:
                        setattr(overwrites, perm, False)
                        await channel.set_permissions(target, overwrite=overwrites)
                        responses.append(
                            f"```{language['permissions_updated']} : {perm}, {channel.name} {language['for']} {target.name}```")
                    except:
                        responses.append(
                            f"```{language['invalid_permissions']} : {perm}, {channel.name} {language['for']} {target.name}```")

    else:
        responses.append(
            f"```{language['invalid']}```")

    messageToSend = responses
    command_func = await load_command("sendMessage")
    await command_func(ctx, messageToSend)
