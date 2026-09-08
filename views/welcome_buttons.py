import discord
from discord.ui import View, Button

class WelcomeButtons(View):
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Rules", style=discord.ButtonStyle.primary)
    async def rules_button(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title="Server Rules",
            description="Click the link below to view the rules.",
            color=0x3498db
        )
        embed.add_field(
            name="",
            value="https://starcityroleplay.com/rules",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Sheriff Department", style=discord.ButtonStyle.success)
    async def sheriff_button(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title="Sheriff Department",
            description="Click the link below to learn more.",
            color=0x2ecc71
        )
        embed.add_field(
            name="",
            value="https://starcityroleplay.com/department/sheriff",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)