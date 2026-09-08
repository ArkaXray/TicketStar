import discord
from datetime import datetime, timezone
from config import Config

class EmbedBuilder:
    
    @staticmethod
    def create(title, description, color=Config["COLORS"]["Primary"], footer="Sheriff Department", timestamp=True):
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now(timezone.utc) if timestamp else None
        )
        embed.set_footer(text=footer)
        return embed
    
    @staticmethod
    def success(title, description):
        return EmbedBuilder.create(title, description, Config["COLORS"]["Success"])
    
    @staticmethod
    def error(title, description):
        return EmbedBuilder.create(title, description, Config["COLORS"]["Error"])
    
    @staticmethod
    def info(title, description):
        return EmbedBuilder.create(title, description, Config["COLORS"]["Info"])
    
    @staticmethod
    def warning(title, description):
        return EmbedBuilder.create(title, description, Config["COLORS"]["Warning"])