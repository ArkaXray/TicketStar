import discord
from discord.ext import commands
from core.ticket_manager import TicketManagerInstance
from config import Config

class Statistics(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="stats")
    async def show_statistics(self, ctx):
        guild = ctx.guild
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        total_tickets, open_tickets, closed_tickets = TicketManagerInstance.get_statistics()
        
        logo_url = "https://starcityroleplay.com/assets/images/logo.png"
        
        embed = discord.Embed(
            title="",
            description=(
                "═══════════════════════════════════════\n"
                "          **SERVER STATISTICS**\n"
                "═══════════════════════════════════════\n\n"
                "**TOTAL MEMBERS**\n"
                f"  {guild.member_count}\n\n"
                "**ONLINE MEMBERS**\n"
                f"  {online_members}\n\n"
                "**OPEN TICKETS**\n"
                f"  {open_tickets}\n\n"
                "**CLOSED TICKETS**\n"
                f"  {closed_tickets}\n\n"
                "**TOTAL TICKETS**\n"
                f"  {total_tickets}\n\n"
                "═══════════════════════════════════════"
            ),
            color=Config["COLORS"]["Info"]
        )
        embed.set_thumbnail(url=logo_url)
        embed.set_footer(text="Sheriff Department")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="help")
    async def show_help(self, ctx):
        logo_url = "https://starcityroleplay.com/assets/images/logo.png"
        
        embed = discord.Embed(
            title="",
            description=(
                "═══════════════════════════════════════\n"
                "            **HELP MENU**\n"
                "═══════════════════════════════════════\n\n"
                "**COMMANDS**\n"
                "─────────────────────────────────────\n"
                "`!ticket`   → Show Ticket Panel\n"
                "             (Admin Only)\n\n"
                "`!stats`    → Server Statistics\n\n"
                "`!help`     → Show This Menu\n\n"
                "`!refresh`  → Refresh Status\n"
                "             (Admin Only)\n\n"
                "`!ping`     → Bot Latency\n"
                "─────────────────────────────────────\n"
                "═══════════════════════════════════════"
            ),
            color=Config["COLORS"]["Primary"]
        )
        embed.set_thumbnail(url=logo_url)
        embed.set_footer(text="Sheriff Department")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Statistics(bot))