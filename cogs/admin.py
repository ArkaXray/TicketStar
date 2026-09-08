import discord
from discord.ext import commands
from utils.embed import embed
from config import CONFIG

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def refresh(self, ctx):
        await ctx.send(embed=embed("✅ Refreshed", "Status updated!", CONFIG["COLORS"]["Success"]))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def status(self, ctx):
        # بروزرسانی استاتوس
        total, open_t, closed_t = 0, 0, 0  # اینو بعداً کامل کن
        
        embed_status = discord.Embed(
            title="Server Status",
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Total Tickets: {total}\n"
                f"Open: {open_t}\n"
                f"Closed: {closed_t}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=CONFIG["COLORS"]["Info"]
        )
        await ctx.send(embed=embed_status)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))