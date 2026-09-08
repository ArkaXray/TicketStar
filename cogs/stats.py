import discord
from discord.ext import commands
from utils.embed import embed
from utils.ticket_manager import ticket_manager
from config import CONFIG

class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stats(self, ctx):
        total, open_t, closed_t = ticket_manager.get_stats()
        online = sum(1 for m in ctx.guild.members if m.status != discord.Status.offline)
        
        embed_stats = discord.Embed(
            title="Server Statistics",
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Total Members: {ctx.guild.member_count}\n"
                f"Online: {online}\n"
                f"Open Tickets: {open_t}\n"
                f"Closed Tickets: {closed_t}\n"
                f"Total Tickets: {total}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=CONFIG["COLORS"]["Info"]
        )
        embed_stats.set_footer(text="SheriffTeam | Statistics")
        
        await ctx.send(embed=embed_stats)

    @commands.command()
    async def help(self, ctx):
        embed_help = discord.Embed(
            title="Help Menu",
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "`!ticket` - Show Ticket Panel (Admin Only)\n"
                "`!stats` - Show Server Statistics\n"
                "`!help` - Show This Menu\n"
                "`!refresh` - Refresh Status Channel (Admin Only)\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=CONFIG["COLORS"]["Primary"]
        )
        embed_help.set_footer(text="SheriffTeam | Help Center")
        await ctx.send(embed=embed_help)

async def setup(bot):
    await bot.add_cog(StatsCog(bot))