import discord
from discord.ext import commands
from core.embed_builder import EmbedBuilder
from config import Config

class Administration(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="refresh")
    @commands.has_permissions(administrator=True)
    async def refresh_status(self, ctx):
        embed = EmbedBuilder.success(
            "Status Refreshed",
            "Server status has been updated."
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="ping")
    async def show_latency(self, ctx):
        latency = round(self.bot.latency * 1000)
        embed = EmbedBuilder.info(
            "Network Latency",
            f"**{latency}ms**"
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Administration(bot))