import discord
from discord.ext import commands
from core.ticket_manager import TicketManagerInstance
from views.welcome_buttons import WelcomeButtons
from config import Config

class EventHandler(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        TicketManagerInstance.add_message(
            message.channel.id,
            message.author.display_name,
            message.author.id,
            message.content
        )
        await self.bot.process_commands(message)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        auto_role = member.guild.get_role(Config["ROLES"]["AutoRole"])
        if auto_role:
            await member.add_roles(auto_role)
        
        welcome_channel = member.guild.get_channel(Config["CHANNELS"]["Welcome"])
        if welcome_channel:
            banner_image = "https://cdn.discordapp.com/attachments/1546881047440920588/1546905048989171833/izvGi.jpg?ex=6aa17b17&is=6aa02997&hm=47dc8926c8328d53e51edf2dd4882ac0769e8abc19ab56a13da802ced2737761&"
            logo_url = "https://starcityroleplay.com/assets/images/logo.webp"
            
            embed = discord.Embed(
                title="",
                description=(
                    "**SHERIFF DEPARTMENT**\n"
                    "**WELCOME**\n\n"
                    f"Hello {member.mention}!\n\n"
                    "Welcome to the Sheriff Department!\n\n"
                    "We're glad to have you here. Please take a moment to\n"
                    "read the rules and choose your roles.\n\n"
                    "**Quick Guide**\n\n"
                    "Read the server rules\n"
                    "Choose your roles from the channels\n"
                    "Use the ticket system for support\n\n"
                    f"Member #{member.guild.member_count}"
                ),
                color=Config["COLORS"]["Gold"]
            )
            embed.set_thumbnail(url=logo_url)
            embed.set_image(url=banner_image)
            embed.set_footer(
                text="Sheriff Department",
                icon_url=logo_url
            )
            
            await welcome_channel.send(
                content=member.mention,
                embed=embed,
                view=WelcomeButtons()
            )

async def setup(bot):
    await bot.add_cog(EventHandler(bot))