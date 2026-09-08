import discord
from datetime import datetime, timezone
from config import CONFIG

def embed(title, desc, color=CONFIG["COLORS"]["Primary"], footer="SheriffTeam | ArkaXray", ts=True):
    e = discord.Embed(
        title=title,
        description=desc,
        color=color,
        timestamp=datetime.now(timezone.utc) if ts else None
    )
    e.set_footer(text=footer)
    return e

def ticket_log_embed(data):
    e = discord.Embed(
        title=f"Ticket Log | {data['ticket_id']}",
        color=CONFIG["COLORS"]["Info"],
        timestamp=datetime.now(timezone.utc)
    )
    e.add_field(name="Title", value=data['title'], inline=False)
    e.add_field(name="Created By", value=f"<@{data['user_id']}>", inline=True)
    e.add_field(name="Type", value=data['type'], inline=True)
    e.add_field(name="Created At", value=data['created_at'], inline=True)
    e.add_field(name="Closed At", value=data['closed_at'] or "Still Open", inline=True)
    e.add_field(name="Status", value=data['status'].capitalize(), inline=True)
    e.add_field(name="Claimed By", value=f"<@{data['claimed_by']}>" if data['claimed_by'] else "Not Claimed", inline=True)

    if data.get('messages'):
        msg_content = "\n".join(
            f"**{m['author']}**: {m['content']}" for m in data['messages'][-5:]
        )
        e.add_field(name="Recent Messages", value=msg_content, inline=False)
    else:
        e.add_field(name="Messages", value="No Messages Recorded", inline=False)

    e.set_footer(text="SheriffTeam | ArkaXray")
    return e