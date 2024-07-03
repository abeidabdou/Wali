import discord
from parameters.channelPermissions import get_permissions
from parameters.guildLanguage import guildLanguage


class WaliSetupManager:
    def __init__(self, guild):
        self.guild = guild
        self.wali_category_name = 'WAL-I'
        self.wali_log_channel_name = 'wal-i-logs'
        self.wali_channel_name = 'wal-i'
        self.language = guildLanguage(guild)
        self.channel_overwrites = get_permissions()

    async def get_or_create_wali_category(self):
        wali_category = discord.utils.get(
            self.guild.categories, name=self.wali_category_name)

        if wali_category is None:
            channel_overwrites = self.channel_overwrites
            overwrites = {
                self.guild.default_role: channel_overwrites
            }
            wali_category = await self.guild.create_category(self.wali_category_name, overwrites=overwrites)

        return wali_category

    async def get_or_create_wali_channel(self):
        wali_channel = discord.utils.get(
            self.guild.text_channels, name=self.wali_channel_name)

        if wali_channel is None:
            channel_overwrites = self.channel_overwrites
            overwrites = {
                self.guild.default_role: channel_overwrites
            }
            wali_channel = await self.guild.create_text_channel(self.wali_channel_name, category=await self.get_or_create_wali_category(), overwrites=overwrites)

        return wali_channel

    async def get_or_create_logs_channel(self):
        wali_log_channel = discord.utils.get(
            self.guild.text_channels, name=self.wali_log_channel_name)

        if wali_log_channel is None:
            channel_overwrites = self.channel_overwrites
            overwrites = {
                self.guild.default_role: channel_overwrites}
            wali_log_channel = await self.guild.create_text_channel(self.wali_log_channel_name, category=await self.get_or_create_wali_category(), overwrites=overwrites)

        return wali_log_channel
