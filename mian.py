import discord
from discord.ext import commands, tasks
from discord.ui import View, Select, Button, Modal, TextInput
import asyncio
import random
from datetime import datetime, timezone
import json
import os
import traceback
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    raise ValueError("No TOKEN found! Please set DISCORD_TOKEN in .env file")

CONFIG = {
    "TOKEN": TOKEN,
    "PREFIX": "!",
    "CATEGORY_IDS": {
        "Ozviat": 1546901402197041273,
        "Shekayat": 1546901482555572264,
        "Enteghali": 1546901558086738003,
        "AdminFaction": 1546901585773334668,
        "Other": 1546901615481589890
    },
    "ROLES": {
        "TicketSup": 1546258768457895986,
        "AutoRole": 1546258763646767195
    },
    "CHANNELS": {
        "TicketPanel": 1546259071529652316,
        "Welcome": 1546881047440920588,
        "Log": 1546902908514205746,
        "Voice": 1546259074876702871,
        "Status": 1546903540528717835
    },
    "COLORS": {
        "Primary": 0x1abc9c,
        "Success": 0x2ecc71,
        "Error": 0xe74c3c,
        "Info": 0x3498db,
        "Warning": 0xf39c12,
        "Dark": 0x2c3e50,
        "Gold": 0xf1c40f,
        "Purple": 0x9b59b6
    }
}

EMOJIS = {
    "admin_faction": "<:267110platino:1540481380209791066>",
    "user": "<:850439snapchatuser:1540481060050305075>",
    "status": "<:124857goodconektion:1540481057932181504>",
    "title": "<:55099creativewriters:1540481055155552367>",
    "note": "<:968958deathnote:1540481053444153384>",
    "date": "<:47836calendar:1540481051481219143>",
    "key": "<:519957cadeadokey:1540481049191125142>",
    "login": "<:94851login:1540481047517593641>",
    "report": "<:18181report:1540481045663711372>",
    "transfer": "<:7234transferir:1540481043872612424>",
    "other": "<:62644roskomnadzor:1540481039988818023>",
    "down": "<:452997downvote:1540481038076354590>",
    "ticket": "<a:437007ticket:1540478194551889920>",
    "danger": "<:89278danger:1540485375145939076>",
    "select": "<:131090select:1540485377092223006>"
}

class TicketManager:
    def __init__(self):
        self.tickets = {}

    def create_ticket(self, tid, uid, ttype, channel_id, title, reason):
        self.tickets[tid] = {
            "ticket_id": tid,
            "title": title,
            "user_id": uid,
            "type": ttype,
            "channel_id": channel_id,
            "reason": reason,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "closed_at": None,
            "status": "open",
            "claimed_by": None,
            "messages": []
        }

    def close_ticket(self, tid):
        if tid in self.tickets:
            self.tickets[tid]["status"] = "closed"
            self.tickets[tid]["closed_at"] = datetime.now(timezone.utc).isoformat()

    def claim_ticket(self, tid, staff_id):
        if tid in self.tickets:
            self.tickets[tid]["claimed_by"] = staff_id

ticket_manager = TicketManager()

def generate_ticket_id():
    return f"T-{random.randint(1000,9999)}"

def embed(title, desc, color=CONFIG["COLORS"]["Primary"], footer="SheriffTeam | ArkaXray", ts=True):
    e = discord.Embed(
        title=f"**{title}**",
        description=desc,
        color=color,
        timestamp=datetime.now(timezone.utc) if ts else None
    )
    e.set_footer(text=footer)
    return e

def embed_ticket_log(tid_data):
    e = discord.Embed(
        title=f"{EMOJIS['ticket']} Ticket Log | {tid_data['ticket_id']}",
        color=CONFIG["COLORS"]["Info"],
        timestamp=datetime.now(timezone.utc)
    )
    e.add_field(name=f"{EMOJIS['title']} Title", value=tid_data['title'], inline=False)
    e.add_field(name=f"{EMOJIS['user']} Created By", value=f"<@{tid_data['user_id']}>", inline=True)
    e.add_field(name=f"{EMOJIS['report']} Type", value=tid_data['type'], inline=True)
    e.add_field(name=f"{EMOJIS['date']} Created At", value=tid_data['created_at'], inline=True)
    e.add_field(name=f"{EMOJIS['key']} Closed At", value=tid_data['closed_at'] or "Still Open", inline=True)
    e.add_field(name=f"{EMOJIS['status']} Status", value=tid_data['status'].capitalize(), inline=True)
    e.add_field(name=f"{EMOJIS['admin_faction']} Claimed By", value=f"<@{tid_data['claimed_by']}>" if tid_data['claimed_by'] else "Not Claimed", inline=True)

    if tid_data['messages']:
        msg_content = ""
        for m in tid_data['messages'][-5:]:
            msg_content += f"**{m['author']}**: {m['content']}\n"
        e.add_field(name=f"{EMOJIS['note']} Recent Messages", value=msg_content, inline=False)
    else:
        e.add_field(name=f"{EMOJIS['note']} Messages", value="No Messages Recorded", inline=False)
    
    e.set_footer(text="SheriffTeam | ArkaXray")
    return e

class TicketModal(Modal):
    def __init__(self, ticket_type: str):
        super().__init__(title="🎫 Create New Ticket")
        self.ticket_type = ticket_type
        self.add_item(TextInput(
            label="📝 Ticket Title",
            style=discord.TextStyle.short,
            placeholder="Enter a descriptive title for your ticket...",
            max_length=100
        ))
        self.add_item(TextInput(
            label="📋 Reason / Description",
            style=discord.TextStyle.paragraph,
            placeholder="Please explain your issue in detail...",
            max_length=1000
        ))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            title = self.children[0].value
            reason = self.children[1].value
            await create_ticket_channel(interaction, self.ticket_type, title, reason)
        except Exception as e:
            print(f"Error in TicketModal: {e}")
            traceback.print_exc()
            await interaction.response.send_message(
                embed=embed(f"{EMOJIS['danger']} Error", f"An Error Occurred:\n{str(e)}", CONFIG["COLORS"]["Error"]),
                ephemeral=True
            )

class TicketPanel(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="🔽 Select Ticket Type...",
        options=[
            discord.SelectOption(
                label="Ozviat", 
                emoji=EMOJIS['user'],
                description="👤 New Membership Request"
            ),
            discord.SelectOption(
                label="Shekayat", 
                emoji=EMOJIS['report'],
                description="📢 Register A Complaint"
            ),
            discord.SelectOption(
                label="Enteghali", 
                emoji=EMOJIS['transfer'],
                description="📦 Transfer Request"
            ),
            discord.SelectOption(
                label="AdminFaction", 
                emoji=EMOJIS['admin_faction'],
                description="👑 Admin Faction Related"
            ),
            discord.SelectOption(
                label="Other", 
                emoji=EMOJIS['other'],
                description="❓ Other Inquiries"
            )
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: Select):
        modal = TicketModal(select.values[0])
        await interaction.response.send_modal(modal)

class TicketControls(View):
    def __init__(self, tid: str, ticket_owner_id: int):
        super().__init__(timeout=None)
        self.tid = tid
        self.ticket_owner_id = ticket_owner_id

    @discord.ui.button(label="👤 Claim", style=discord.ButtonStyle.primary, emoji="👤")
    async def claim(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id == self.ticket_owner_id:
            await interaction.response.send_message(
                embed=embed(f"{EMOJIS['danger']} Cannot Claim", "❌ You Cannot Claim Your Own Ticket", CONFIG["COLORS"]["Error"]),
                ephemeral=True
            )
            return
        ticket_manager.claim_ticket(self.tid, interaction.user.id)
        await interaction.response.send_message(
            embed=embed(f"{EMOJIS['status']} Ticket Claimed", f"✅ Ticket Claimed By {interaction.user.mention}", CONFIG["COLORS"]["Success"])
        )
        button.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: Button):
        try:
            ticket_manager.close_ticket(self.tid)
            for i in self.children:
                i.disabled = True
            await interaction.response.send_message(
                embed=embed(f"{EMOJIS['danger']} Ticket Closed", "🔒 Preparing Full JSON Log...", CONFIG["COLORS"]["Warning"])
            )
            await interaction.message.edit(view=self)

            tid_data = ticket_manager.tickets[self.tid]
            file_path = f"{self.tid}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(tid_data, f, indent=4, ensure_ascii=False)

            guild = interaction.guild
            log_channel = guild.get_channel(CONFIG["CHANNELS"]["Log"])
            user = guild.get_member(tid_data["user_id"])

            if log_channel:
                await log_channel.send(
                    embed=embed_ticket_log(tid_data),
                    file=discord.File(file_path, filename=f"{self.tid}.json")
                )

            if user:
                try:
                    await user.send(
                        embed=embed_ticket_log(tid_data),
                        file=discord.File(file_path, filename=f"{self.tid}.json")
                    )
                except:
                    print(f"Could Not Send DM To {user.name}")

            await asyncio.sleep(5)
            await interaction.channel.delete()
            os.remove(file_path)
            
        except Exception as e:
            print(f"Error Closing Ticket: {e}")
            traceback.print_exc()

async def create_ticket_channel(interaction: discord.Interaction, ttype: str, title: str, reason: str):
    try:
        guild = interaction.guild
        user = interaction.user
        tid = generate_ticket_id()
        
        category_id = CONFIG["CATEGORY_IDS"].get(ttype)
        if not category_id:
            await interaction.response.send_message(
                embed=embed(f"{EMOJIS['danger']} Error", f"❌ Category Not Found For {ttype}!", CONFIG["COLORS"]["Error"]),
                ephemeral=True
            )
            return
            
        category = guild.get_channel(category_id)
        if not category or not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message(
                embed=embed(
                    f"{EMOJIS['danger']} Error", 
                    f"❌ Category Not Found! (ID: {category_id})\nPlease Contact Admin.",
                    CONFIG["COLORS"]["Error"]
                ),
                ephemeral=True
            )
            print(f"Category Not Found: ID={category_id}, Type={type(category)}")
            return

        ticket_sup_role = guild.get_role(CONFIG["ROLES"]["TicketSup"])
        if not ticket_sup_role:
            await interaction.response.send_message(
                embed=embed(
                    f"{EMOJIS['danger']} Error",
                    "❌ Ticket Support Role Not Found! Please Contact Admin.",
                    CONFIG["COLORS"]["Error"]
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
            name=f"{ttype}-{tid}",
            overwrites=overwrites,
            topic=f"Ticket {ttype} For {user.display_name}"
        )
        
        ticket_manager.create_ticket(tid, user.id, ttype, channel.id, title, reason)

        try:
            await interaction.response.send_message(
                embed=embed(f"{EMOJIS['status']} Ticket Created", f"✅ Go To {channel.mention}", CONFIG["COLORS"]["Success"]),
                ephemeral=True
            )
        except discord.InteractionResponded:
            await interaction.followup.send(
                embed=embed(f"{EMOJIS['status']} Ticket Created", f"✅ Go To {channel.mention}", CONFIG["COLORS"]["Success"]),
                ephemeral=True
            )

        await channel.send(
            content=f"{user.mention} | <@&{CONFIG['ROLES']['TicketSup']}>",
            embed=embed(
                f"{EMOJIS['ticket']} {title}",
                f"**Hello {user.mention}!**\n**Reason:**\n{reason}",
                CONFIG["COLORS"]["Primary"]
            ),
            view=TicketControls(tid, user.id)
        )
        
        print(f"Ticket Created: {tid} By {user.name}")
        
    except Exception as e:
        print(f"Error Creating Ticket: {e}")
        traceback.print_exc()
        try:
            await interaction.response.send_message(
                embed=embed(f"{EMOJIS['danger']} Error", f"❌ An Error Occurred:\n{str(e)}", CONFIG["COLORS"]["Error"]),
                ephemeral=True
            )
        except:
            pass

async def send_ticket_panel(bot):
    try:
        channel = bot.get_channel(CONFIG["CHANNELS"]["TicketPanel"])
        if not channel:
            print(f"TicketPanel Channel Not Found! ID: {CONFIG['CHANNELS']['TicketPanel']}")
            return

        async for message in channel.history(limit=100):
            if message.author == bot.user:
                await message.delete()
                await asyncio.sleep(0.5)

        embed_panel = discord.Embed(
            title=f"{EMOJIS['ticket']} **Ticket System**",
            description=(
                "**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
                "**📌 How To Create A Ticket:**\n"
                "• Select your ticket type from the menu below\n"
                "• Fill in the title and description\n"
                "• Wait for support team to assist you\n\n"
                "**🔹 Ticket Types:**\n"
                f"{EMOJIS['user']} **Ozviat** → New Membership Request\n"
                f"{EMOJIS['report']} **Shekayat** → Register A Complaint\n"
                f"{EMOJIS['transfer']} **Enteghali** → Transfer Request\n"
                f"{EMOJIS['admin_faction']} **AdminFaction** → Admin Related\n"
                f"{EMOJIS['other']} **Other** → Other Inquiries\n\n"
                "**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
                "⚡ **Select Your Ticket Type Below**\n"
                "**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**"
            ),
            color=CONFIG["COLORS"]["Primary"],
            timestamp=datetime.now(timezone.utc)
        )
        embed_panel.set_footer(text="SheriffTeam | Support System", icon_url=bot.user.display_avatar.url)

        await channel.send(embed=embed_panel, view=TicketPanel())
        print(f"Ticket Panel Auto-Sent In {channel.name}")
        
    except Exception as e:
        print(f"Error Sending Ticket Panel: {e}")
        traceback.print_exc()

async def update_status(bot):
    try:
        channel = bot.get_channel(CONFIG["CHANNELS"]["Status"])
        if not channel:
            print(f"Status Channel Not Found! ID: {CONFIG['CHANNELS']['Status']}")
            return

        async for message in channel.history(limit=10):
            if message.author == bot.user:
                await message.delete()
                await asyncio.sleep(0.5)

        open_tickets = sum(1 for t in ticket_manager.tickets.values() if t["status"] == "open")
        closed_tickets = sum(1 for t in ticket_manager.tickets.values() if t["status"] == "closed")
        total_tickets = len(ticket_manager.tickets)
        
        guild = channel.guild
        total_members = guild.member_count
        online_members = sum(1 for m in guild.members if m.status != discord.Status.offline)
        
        embed_status = discord.Embed(
            title=f"{EMOJIS['status']} **Server Status**",
            description=(
                "**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
                f"**👥 Members:**\n"
                f"> • Total: **{total_members}**\n"
                f"> • Online: **{online_members}**\n\n"
                f"**🎫 Tickets:**\n"
                f"> • Open: **{open_tickets}**\n"
                f"> • Closed: **{closed_tickets}**\n"
                f"> • Total: **{total_tickets}**\n"
                "**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
                f"🕐 **Last Updated:** <t:{int(datetime.now(timezone.utc).timestamp())}:R>"
            ),
            color=CONFIG["COLORS"]["Info"],
            timestamp=datetime.now(timezone.utc)
        )
        embed_status.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed_status.set_footer(text="SheriffTeam | Live Status", icon_url=bot.user.display_avatar.url)

        await channel.send(embed=embed_status)
        print(f"Status Updated In {channel.name}")
        
    except Exception as e:
        print(f"Error Updating Status: {e}")
        traceback.print_exc()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=CONFIG["PREFIX"], intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"{bot.user} Ready!")
    print(f"Connected To {len(bot.guilds)} Guilds")
    print(f"Watching {len(bot.users)} Users")
    
    status_loop.start()
    status_update_loop.start()
    
    await send_ticket_panel(bot)
    await update_status(bot)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    try:
        for tid, data in ticket_manager.tickets.items():
            if data["channel_id"] == message.channel.id and data["status"] == "open":
                data["messages"].append({
                    "author": message.author.name,
                    "author_id": message.author.id,
                    "content": message.content,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
    except Exception as e:
        print(f"Error In On_Message: {e}")
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    try:
        auto_role = member.guild.get_role(CONFIG["ROLES"]["AutoRole"])
        if auto_role:
            await member.add_roles(auto_role)
        
        channel = member.guild.get_channel(CONFIG["CHANNELS"]["Welcome"])
        if channel:
            welcome_banner = "https://cdn.discordapp.com/attachments/1546881047440920588/1546905048989171833/izvGi.jpg"
            
            embed_welcome = discord.Embed(
                title=f"{EMOJIS['status']} **Welcome To The Server!**",
                description=(
                    f"**Hello {member.mention}!** 👋\n"
                    f"Welcome To **{member.guild.name}**!\n\n"
                    f"📌 **Quick Guide:**\n"
                    f"> • Read The Rules\n"
                    f"> • Choose Your Roles\n"
                    f"> • Use Ticket System For Support\n\n"
                    f"🎉 **We Hope You Enjoy Your Stay!**"
                ),
                color=CONFIG["COLORS"]["Success"],
                timestamp=datetime.now(timezone.utc)
            )
            embed_welcome.set_image(url=welcome_banner)
            embed_welcome.set_footer(
                text=f"SheriffTeam | Member #{member.guild.member_count}",
                icon_url=member.guild.icon.url if member.guild.icon else None
            )
            
            await channel.send(
                content=f"{member.mention} 🎉",
                embed=embed_welcome
            )
        
        print(f"New Member Joined: {member.name}")
        await update_status(bot)
        
    except Exception as e:
        print(f"Error In On_Member_Join: {e}")
        traceback.print_exc()

@bot.event
async def on_member_remove(member):
    try:
        await update_status(bot)
    except Exception as e:
        print(f"Error In On_Member_Remove: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            embed=embed(
                f"{EMOJIS['danger']} Access Denied",
                "❌ You Don't Have Permission To Use This Command!",
                CONFIG["COLORS"]["Error"]
            )
        )
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(
            embed=embed(
                f"{EMOJIS['danger']} Command Not Found",
                f"❌ Command `{ctx.message.content}` Not Found!\nUse `!help` To See Available Commands.",
                CONFIG["COLORS"]["Error"]
            )
        )
    else:
        print(f"Command Error: {error}")
        await ctx.send(
            embed=embed(
                f"{EMOJIS['danger']} Error",
                f"❌ An Error Occurred:\n{str(error)}",
                CONFIG["COLORS"]["Error"]
            )
        )

@tasks.loop(minutes=5)
async def status_loop():
    try:
        activities = [
            discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.users)} Users"),
            discord.Activity(type=discord.ActivityType.listening, name=f"{len(bot.guilds)} Servers"),
            discord.Activity(type=discord.ActivityType.playing, name="!help"),
        ]
        await bot.change_presence(activity=random.choice(activities))
    except Exception as e:
        print(f"Error In Status Loop: {e}")

@tasks.loop(minutes=2)
async def status_update_loop():
    await update_status(bot)

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    try:
        async for message in ctx.channel.history(limit=100):
            if message.author == bot.user:
                await message.delete()
                await asyncio.sleep(0.5)

        embed_panel = discord.Embed(
            title=f"{EMOJIS['ticket']} **Ticket System**",
            description=(
                "**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
                "**📌 How To Create A Ticket:**\n"
                "• Select your ticket type from the menu below\n"
                "• Fill in the title and description\n"
                "• Wait for support team to assist you\n\n"
                "**🔹 Ticket Types:**\n"
                f"{EMOJIS['user']} **Ozviat** → New Membership Request\n"
                f"{EMOJIS['report']} **Shekayat** → Register A Complaint\n"
                f"{EMOJIS['transfer']} **Enteghali** → Transfer Request\n"
                f"{EMOJIS['admin_faction']} **AdminFaction** → Admin Related\n"
                f"{EMOJIS['other']} **Other** → Other Inquiries\n\n"
                "**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
                "⚡ **Select Your Ticket Type Below**\n"
                "**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**"
            ),
            color=CONFIG["COLORS"]["Primary"],
            timestamp=datetime.now(timezone.utc)
        )
        embed_panel.set_footer(text="SheriffTeam | Support System", icon_url=bot.user.display_avatar.url)

        await ctx.send(embed=embed_panel, view=TicketPanel())
        print(f"Ticket Panel Shown By {ctx.author.name}")
    except Exception as e:
        print(f"Error In Ticket Command: {e}")
        await ctx.send(embed=embed(f"{EMOJIS['danger']} Error", str(e), CONFIG["COLORS"]["Error"]))

@bot.command()
async def stats(ctx):
    try:
        g = ctx.guild
        open_t = sum(1 for t in ticket_manager.tickets.values() if t["status"] == "open")
        closed_t = sum(1 for t in ticket_manager.tickets.values() if t["status"] == "closed")
        online = sum(1 for m in g.members if m.status != discord.Status.offline)
        
        embed_stats = discord.Embed(
            title=f"{EMOJIS['status']} **Server Statistics**",
            description=(
                "**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
                f"{EMOJIS['user']} **Total Members:** {g.member_count}\n"
                f"🟢 **Online:** {online}\n"
                f"{EMOJIS['status']} **Open Tickets:** {open_t}\n"
                f"{EMOJIS['key']} **Closed Tickets:** {closed_t}\n"
                f"{EMOJIS['ticket']} **Total Tickets:** {len(ticket_manager.tickets)}\n"
                "**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**"
            ),
            color=CONFIG["COLORS"]["Info"],
            timestamp=datetime.now(timezone.utc)
        )
        embed_stats.set_footer(text="SheriffTeam | Statistics")
        
        await ctx.send(embed=embed_stats)
    except Exception as e:
        print(f"Error In Stats Command: {e}")
        await ctx.send(embed=embed(f"{EMOJIS['danger']} Error", str(e), CONFIG["COLORS"]["Error"]))

@bot.command()
@commands.has_permissions(administrator=True)
async def refresh(ctx):
    try:
        await update_status(bot)
        await ctx.send(embed=embed("✅ Status Refreshed", "Status channel has been updated!", CONFIG["COLORS"]["Success"]))
    except Exception as e:
        await ctx.send(embed=embed(f"{EMOJIS['danger']} Error", str(e), CONFIG["COLORS"]["Error"]))

@bot.command()
async def help(ctx):
    try:
        embed_help = discord.Embed(
            title=f"{EMOJIS['login']} **Help Menu**",
            description=(
                "**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
                f"{EMOJIS['ticket']} `!ticket` - Show Ticket Panel (Admin Only)\n"
                f"{EMOJIS['status']} `!stats` - Show Server Statistics\n"
                f"{EMOJIS['login']} `!help` - Show This Menu\n"
                f"🔄 `!refresh` - Refresh Status Channel (Admin Only)\n"
                "**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**"
            ),
            color=CONFIG["COLORS"]["Primary"],
            timestamp=datetime.now(timezone.utc)
        )
        embed_help.set_footer(text="SheriffTeam | Help Center")
        
        await ctx.send(embed=embed_help)
    except Exception as e:
        print(f"Error In Help Command: {e}")
        await ctx.send(embed=embed(f"{EMOJIS['danger']} Error", str(e), CONFIG["COLORS"]["Error"]))

if __name__ == "__main__":
    try:
        print("Starting Bot...")
        bot.run(CONFIG["TOKEN"])
    except discord.LoginFailure:
        print("Invalid Token! Please Enter A Valid Token.")
    except Exception as e:
        print(f"Error Starting Bot: {e}")
        traceback.print_exc()