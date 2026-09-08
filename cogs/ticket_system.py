import discord
from discord.ext import commands
from core.ticket_manager import TicketManagerInstance
from views.ticket_controls import TicketControls
from config import Config
import traceback

class TicketSystem(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.ticket_manager = TicketManagerInstance
    
    @commands.command(name="ticket")
    @commands.has_permissions(administrator=True)
    async def create_ticket_panel(self, ctx):
        await self._send_panel(ctx.channel)
    
    async def _send_panel(self, channel):
        await channel.purge(limit=100, check=lambda message: message.author == self.bot.user)
        
        banner_image = "https://cdn.discordapp.com/attachments/1546259114387177496/1546952327037067445/sheriffticket.png"
        logo_url = "https://starcityroleplay.com/assets/images/logo.webp"
        
        embed = discord.Embed(
            title="",
            description=(
                "**SHERIFF DEPARTMENT**\n"
                "**TICKET SYSTEM**\n\n"
                "Welcome to the Sheriff Department Support Channel!\n\n"
                "We're glad to have you here. If you need assistance, you're in the\n"
                "right place - our support team is ready to help you.\n\n"
                "**OZVIAT**\n"
                "New Membership Request\n\n"
                "**SHEKAYAT**\n"
                "Register a Complaint\n\n"
                "**ENTEGHALI**\n"
                "Transfer Request\n\n"
                "**CHIEF OF SHERIFF**\n"
                "Chief Related Matters\n\n"
                "**OTHER**\n"
                "Other Inquiries\n\n"
                "**Important Notice**\n\n"
                "All tickets are logged and reviewed — please do not open tickets\n"
                "unnecessarily. Make sure to select the correct category for your\n"
                "issue. After selecting your option, a new form will open -\n"
                "please fill it out carefully and completely."
            ),
            color=Config["COLORS"]["Gold"]
        )
        embed.set_thumbnail(url=logo_url)
        embed.set_image(url=banner_image)
        embed.set_footer(
            text="Sheriff Department | Support System",
            icon_url=logo_url
        )
        
        from views.ticket_panel import TicketPanel
        await channel.send(embed=embed, view=TicketPanel())
        print(f"Ticket panel sent to {channel.name}")

async def create_ticket_channel(interaction: discord.Interaction, ttype: str, title: str, reason: str):
    try:
        guild = interaction.guild
        user = interaction.user
        tid = TicketManagerInstance.generate_ticket_id()
        
        # Map ticket type to category
        category_map = {
            "Ozviat": "Ozviat",
            "Shekayat": "Shekayat",
            "Enteghali": "Enteghali",
            "Chief Of Sheriff": "AdminFaction",
            "Other": "Other"
        }
        
        category_key = category_map.get(ttype, "Other")
        category_id = Config["CATEGORY_IDS"].get(category_key)
        
        if not category_id:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error",
                    description=f"Category not found for {ttype}!",
                    color=Config["COLORS"]["Error"]
                ),
                ephemeral=True
            )
            return
            
        category = guild.get_channel(category_id)
        if not category or not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error", 
                    description="Category not found! Please contact an admin.",
                    color=Config["COLORS"]["Error"]
                ),
                ephemeral=True
            )
            return

        # Debug: Print all roles to check
        print("Available roles in config:", Config["ROLES"].keys())
        print("Looking for role ID:", Config["ROLES"].get("TicketSup"))
        
        ticket_sup_role = guild.get_role(Config["ROLES"]["TicketSup"])
        if not ticket_sup_role:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error",
                    description="Ticket support role not found! Please contact an admin.",
                    color=Config["COLORS"]["Error"]
                ),
                ephemeral=True
            )
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(
                view_channel=True, 
                send_messages=True, 
                read_message_history=True
            ),
            ticket_sup_role: discord.PermissionOverwrite(
                view_channel=True, 
                send_messages=True, 
                manage_channels=True, 
                manage_messages=True
            )
        }

        channel = await category.create_text_channel(
            name=f"{ttype.lower()}-{tid}",
            overwrites=overwrites,
            topic=f"Ticket {ttype} For {user.display_name}"
        )
        
        TicketManagerInstance.create_ticket(tid, user.id, ttype, channel.id, title, reason)

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Ticket Created",
                description=f"Go to {channel.mention}",
                color=Config["COLORS"]["Success"]
            ),
            ephemeral=True
        )

        await channel.send(
            content=f"{user.mention} | <@&{Config['ROLES']['TicketSup']}>",
            embed=discord.Embed(
                title=title,
                description=f"Hello {user.mention}!\n\nReason:\n{reason}",
                color=Config["COLORS"]["Primary"]
            ),
            view=TicketControls(tid, user.id, TicketManagerInstance)
        )
        
        print(f"Ticket created: {tid} by {user.name}")
        
    except Exception as e:
        print(f"Error creating ticket: {e}")
        traceback.print_exc()
        try:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error",
                    description=f"An error occurred:\n{str(e)}",
                    color=Config["COLORS"]["Error"]
                ),
                ephemeral=True
            )
        except:
            pass

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))