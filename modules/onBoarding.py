import asyncio
import time
import discord
from discord.ext import commands
import discord
import re
from command.loadCommand import load_command


def OnBoardingEmbed(language, embed_color, status):

    onboarding_embed = discord.Embed(
        title=language['onboarding_current_state_name'],
        description=f'{status}',
        color=embed_color
    )

    return onboarding_embed

def OnBoardingChannelEmbed(language, embed_color, channel_name):

    onboarding_embed = discord.Embed(
        title=language['onboarding_channel_selection'],
        description=channel_name,
        color=embed_color
    )

    return onboarding_embed

def OnBoardedMemberRoleEmbed(language, embed_color, role_name):

    onboarding_embed = discord.Embed(
        title=language['onboarded_member_role'],
        description='None',
        color=embed_color
    )

    return onboarding_embed

class OnboardingToggleButton(discord.ui.Button):
    def __init__(self, language):
        super().__init__(style=discord.ButtonStyle.green,
                         label=language['switch_on'], emoji='🏁', custom_id='onboarding_toggle_button')
        self.language = language

    async def callback(self, interaction: discord.Interaction):

        embeds = interaction.message.embeds

        if embeds:
            fields = embeds[0].description

            if fields:
                status_value = fields
                self.view.value = False if status_value.lower(
                ) == self.language['on'].lower() else True

        self.style = discord.ButtonStyle.red if self.view.value else discord.ButtonStyle.green
        self.label = self.language['switch_off'] if self.view.value else self.language['switch_on']
        self.emoji = '⚔️' if self.view.value else '🏁'
        embed_color = discord.Color.green() if self.view.value else discord.Color.red()
        async for message in interaction.channel.history(limit=None):
            if message.author == interaction.client.user and message.embeds and message.id != interaction.message.id:
                embed = message.embeds[0]
                embed.color = embed_color
                await message.edit(embed=embed)
        status = self.language['on'] if self.view.value else self.language['off']
        await interaction.response.edit_message(embed=OnBoardingEmbed(self.language, embed_color, status), view=self.view)

class OnboardingView(discord.ui.View):
    def __init__(self, language):
        super().__init__(timeout=None)
        self.value = False
        self.language = language
        self.button = OnboardingToggleButton(language)
        self.add_item(self.button)

    async def on_add_item(self, item):
        if isinstance(item, OnboardingToggleButton):
            item.style = discord.ButtonStyle.red if self.value else discord.ButtonStyle.green
            item.label = self.language['switch_off'] if self.value else self.language['switch_on']
            item.emoji = '⚔️' if self.value else '🏁'


class OnboardingPassCodeButton(discord.ui.Button):
    def __init__(self, language):
        super().__init__(style=discord.ButtonStyle.gray,
                         label=language['pass_code'], emoji='➕', custom_id='onboarding_passcode_button')

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

class OnboardingJoinMethodView(discord.ui.View):
    def __init__(self, language):
        super().__init__(timeout=None)
        self.language = language
        self.add_item(OnboardingPassCodeButton(language))

class OnboardingCreateChannelButton(discord.ui.Button):
    def __init__(self, language):
        super().__init__(style=discord.ButtonStyle.gray,
                         label=language['create_onboarding_channel'], emoji='➕', custom_id='create_onboarding_channel')
        self.language = language

    async def callback(self, interaction: discord.Interaction):

        channel_name = None

        await interaction.response.send_message(f"```{self.language['onboarding_channel_creation_instructions']}```")

        def check(m):
            return m.channel == interaction.channel and m.author == interaction.user

        timeout = time.time() + 60.0
        channel_name = None

        while time.time() < timeout and channel_name is None:
            try:
                message = await asyncio.wait_for(interaction.client.wait_for('message', check=check), timeout=timeout - time.time())
                channel_name = message.content
                command = f'createChannel["{message.content}"] type("text") visibility("public")'
                command_name = "createChannel"
                command_func = await load_command(command_name)
                channel = await command_func(message, command)
                channel_to_use = channel.name
                async for message in interaction.channel.history(limit=None):
                    if message.author == interaction.client.user and message.embeds:
                        embed = message.embeds[0]
                        if embed.title == self.language['onboarding_channel_selection']:
                            embed.description = channel_to_use
                            await message.edit(embed=embed)
                            await interaction.followup.send(f"```{self.language['onboarding_channel_added_message']}```", ephemeral=True)
            except asyncio.TimeoutError:
                break

        if channel_name is None:
            await interaction.followup.send(f"```{self.language['onboarding_channel_creation_timeout_message']}```", ephemeral=True)

        await interaction.delete_original_response()

class ChannelButton(discord.ui.Button):
    def __init__(self, channel, language):
        super().__init__(style=discord.ButtonStyle.gray, label=channel.name, custom_id=f'channel_{channel.id}')
        self.channel = channel
        self.language = language

    async def callback(self, interaction: discord.Interaction):
       await interaction.response.defer()
       async for message in interaction.channel.history(limit=None):
            if message.author == interaction.client.user and message.embeds:
                embed = message.embeds[0]
                if embed.title == self.language['onboarding_channel_selection']:
                    embed.description = self.channel.name
                    await message.edit(embed=embed)
                    await interaction.followup.send(f"```{self.language['onboarding_channel_added_message']}```", ephemeral=True)
        
class OnboardingChannelSelectButton(discord.ui.Button):
    def __init__(self, language):
        super().__init__(style=discord.ButtonStyle.gray,
                         label=language['onboarding_channel_selection_placeholder'], emoji='⛏️', custom_id='onboarding_channel_select_button')
        self.language = language

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channels = [channel for channel in interaction.guild.text_channels]

        view = discord.ui.View()
        if channels:
            for channel in channels:
                view.add_item(ChannelButton(channel, self.language))

            await interaction.followup.send(f"```{self.language['choose_onboarding_channel']}```", view=view, ephemeral=True)
        else:
            await interaction.followup.send(f"```{self.language['no_text_channels']}```", ephemeral=True)

class OnboardingRoleButton(discord.ui.Button):
    def __init__(self, language):
        super().__init__(style=discord.ButtonStyle.gray,
                         label=language['onboarded_member_role_placeholder'], emoji='⛏️', custom_id='onboarded_member_role_placeholder')

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

class OnboardingRoleSelectView(discord.ui.View):
    def __init__(self, language):
        super().__init__(timeout=None)
        self.language = language
        self.add_item(OnboardingRoleButton(language))

class OnboardingChannelSelectionView(discord.ui.View):
    def __init__(self, language):
        super().__init__(timeout=None)
        self.language = language
        self.add_item(OnboardingCreateChannelButton(language))
        self.add_item(OnboardingChannelSelectButton(language))

async def onBoarding(channel, language):

    embed_color = discord.Color.red()
    status = language['off']
    channel_name = language['obonarding_none_value']
    role_name = language['obonarding_none_value']

    onboardingView = OnboardingView(language)

    loginMethodView = OnboardingJoinMethodView(language)

    channelSelectionView = OnboardingChannelSelectionView(language)

    roleSelectionView = OnboardingRoleSelectView(language)

    await channel.send(f"```{language['onboarding_module_description_message']}```", view=onboardingView, embed=OnBoardingEmbed(language, embed_color, status))

    await channel.send(f"```{language['choose_member_onboarding_channel']}```", view=channelSelectionView, embed=OnBoardingChannelEmbed(language, embed_color, channel_name))

    await channel.send(f"```{language['choose_onboarded_member_role']}```", view=roleSelectionView, embed=OnBoardedMemberRoleEmbed(language, embed_color, role_name))

    await channel.send(view=loginMethodView)
