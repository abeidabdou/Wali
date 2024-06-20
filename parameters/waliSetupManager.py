import discord
from parameters.channelPermissions import get_permissions
from parameters.guildLanguage import guildLanguage
from parameters.rolePermissions import get_roles_permissions


class WaliSetupManager:
    def __init__(self, guild):
        self.guild = guild
        self.wali_category_name = 'WAL-I'
        self.wali_log_channel_name = 'wal-i-logs'
        self.wali_channel_name = 'wal-i'
        self.wali_mods_role_name = 'wal-i-mod'
        self.language = guildLanguage(guild)
        self.wali_mods_channel_name = 'wal-i-mods'
        self.channel_overwrites = get_permissions()

    async def get_or_create_mod_role(self):
        wali_mods_role = discord.utils.get(
            self.guild.roles, name=self.wali_mods_role_name)

        mods_permission = get_roles_permissions()

        if wali_mods_role is None:
            wali_mods_role = await self.guild.create_role(name=self.wali_mods_role_name, permissions=mods_permission)
            for channel in self.guild.text_channels:
                await channel.set_permissions(wali_mods_role, use_application_commands=True)

        return wali_mods_role

    async def get_or_create_wali_category(self):
        wali_category = discord.utils.get(
            self.guild.categories, name=self.wali_category_name)

        wali_mods_role = await self.get_or_create_mod_role()

        if wali_category is None:
            channel_overwrites = self.channel_overwrites
            overwrites = {
                self.guild.default_role: channel_overwrites,
                wali_mods_role: discord.PermissionOverwrite(
                    read_messages=True, send_messages=True, read_message_history=True, use_application_commands=True)
            }
            wali_category = await self.guild.create_category(self.wali_category_name, overwrites=overwrites)

        return wali_category

    async def get_or_create_wali_channel(self):
        wali_channel = discord.utils.get(
            self.guild.text_channels, name=self.wali_channel_name)

        wali_mods_role = await self.get_or_create_mod_role()

        if wali_channel is None:
            channel_overwrites = self.channel_overwrites
            overwrites = {
                self.guild.default_role: channel_overwrites,
                wali_mods_role: discord.PermissionOverwrite(
                    read_messages=False, send_messages=False, read_message_history=False)
            }
            wali_channel = await self.guild.create_text_channel(self.wali_channel_name, category=await self.get_or_create_wali_category(), overwrites=overwrites)
            pin_message = await wali_channel.send(f"`{self.language['wali_channel_pinned_message']}`")
            await pin_message.pin()

        return wali_channel

    async def get_or_create_logs_channel(self):
        wali_log_channel = discord.utils.get(
            self.guild.text_channels, name=self.wali_log_channel_name)
        wali_mods_role = await self.get_or_create_mod_role()
        if wali_log_channel is None:
            channel_overwrites = self.channel_overwrites
            overwrites = {
                self.guild.default_role: channel_overwrites,
                wali_mods_role: discord.PermissionOverwrite(
                    read_messages=False, send_messages=False, read_message_history=False)
            }
            wali_log_channel = await self.guild.create_text_channel(self.wali_log_channel_name, category=await self.get_or_create_wali_category(), overwrites=overwrites)

        return wali_log_channel

    async def get_or_create_wali_mods_channel(self):
        wali_mods_channel = discord.utils.get(
            self.guild.text_channels, name=self.wali_mods_channel_name)
        wali_mods_role = await self.get_or_create_mod_role()
        if wali_mods_channel is None:
            channel_overwrites = self.channel_overwrites
            overwrites = {
                self.guild.default_role: channel_overwrites,
                wali_mods_role: discord.PermissionOverwrite(
                    read_messages=False, send_messages=False, read_message_history=False)
            }
            wali_mods_channel = await self.guild.create_text_channel(self.wali_mods_channel_name, category=await self.get_or_create_wali_category(), overwrites=overwrites)

        return wali_mods_channel

    async def get_or_create_mod_channel(self):
        mod_channel_name = f"wal-i-mods-channel"
        mod_channel = discord.utils.get(
            self.guild.text_channels, name=mod_channel_name)

        if mod_channel is None:
            mod_channel = await self.guild.create_text_channel(mod_channel_name, category=await self.get_or_create_wali_category())
            pin_message = await mod_channel.send(f"`{self.language['wali_mod_channel_pinned_message']}`")
            await pin_message.pin()

        return mod_channel
