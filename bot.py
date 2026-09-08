import discord
from discord.ext import commands, tasks
from config import Config
from views.ticket_panel import TicketPanel
import asyncio
import traceback
import os
import sys

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=Config["PREFIX"],
    intents=intents,
    help_command=None
)

async def load_extensions():
    extensions = [
        "cogs.ticket_system",
        "cogs.event_handler",
        "cogs.statistics",
        "cogs.administration"
    ]
    
    for extension in extensions:
        try:
            await bot.load_extension(extension)
            print(f"Loaded: {extension}")
        except Exception as error:
            print(f"Failed to load {extension}: {error}")

async def send_ticket_panel():
    try:
        channel_id = Config["CHANNELS"]["TicketPanel"]
        channel = bot.get_channel(channel_id)
        
        if not channel:
            print(f"Channel not found: {channel_id}")
            return
        
        # Clear old messages
        async for message in channel.history(limit=100):
            if message.author == bot.user:
                try:
                    await message.delete()
                    await asyncio.sleep(0.2)
                except:
                    pass
        
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

        await channel.send(embed=embed, view=TicketPanel())
        print(f"Ticket panel sent to {channel.name}")
        
    except Exception as error:
        print(f"Error sending ticket panel: {error}")

@bot.event
async def on_ready():
    print(f"Bot is online: {bot.user}")
    print(f"Connected to {len(bot.guilds)} guilds")
    print(f"Bot is running on Railway!")
    
    await load_extensions()
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Sheriff Department"
        )
    )
    
    await asyncio.sleep(5)
    await send_ticket_panel()
    
    # Start loops
    try:
        panel_check_loop.start()
        status_loop.start()
    except RuntimeError:
        # Loop already running
        pass

@tasks.loop(minutes=10)
async def panel_check_loop():
    try:
        channel_id = Config["CHANNELS"]["TicketPanel"]
        channel = bot.get_channel(channel_id)
        if channel:
            panel_exists = False
            async for message in channel.history(limit=50):
                if message.author == bot.user:
                    if message.embeds and message.components:
                        panel_exists = True
                        break
            
            if not panel_exists:
                print("Panel message not found! Resending...")
                await send_ticket_panel()
    except Exception as error:
        print(f"Error in panel check: {error}")

@tasks.loop(minutes=5)
async def status_loop():
    try:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Sheriff Department"
            )
        )
    except Exception as error:
        print(f"Error in status loop: {error}")

@panel_check_loop.before_loop
async def before_panel_check():
    await bot.wait_until_ready()

@status_loop.before_loop
async def before_status():
    await bot.wait_until_ready()

if __name__ == "__main__":
    try:
        print("Starting bot on Railway...")
        bot.run(Config["TOKEN"])
    except discord.LoginFailure:
        print("Invalid token provided")
        sys.exit(1)
    except Exception as error:
        print(f"Error starting bot: {error}")
        traceback.print_exc()
        sys.exit(1)