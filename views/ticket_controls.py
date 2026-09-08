import discord
from discord.ui import View, Button
from config import Config
import json
import os
import asyncio
import traceback

def embed_ticket_log(tid_data):
    e = discord.Embed(
        title=f"Ticket Log | {tid_data['ticket_id']}",
        color=Config["COLORS"]["Info"]
    )
    e.add_field(name="Title", value=tid_data['title'], inline=False)
    e.add_field(name="Created By", value=f"<@{tid_data['user_id']}>", inline=True)
    e.add_field(name="Type", value=tid_data['type'], inline=True)
    e.add_field(name="Created At", value=tid_data['created_at'], inline=True)
    e.add_field(name="Closed At", value=tid_data['closed_at'] or "Still Open", inline=True)
    e.add_field(name="Status", value=tid_data['status'].capitalize(), inline=True)
    e.add_field(name="Claimed By", value=f"<@{tid_data['claimed_by']}>" if tid_data['claimed_by'] else "Not Claimed", inline=True)

    if tid_data['messages']:
        msg_content = ""
        for m in tid_data['messages'][-5:]:
            msg_content += f"**{m['author']}**: {m['content']}\n"
        e.add_field(name="Recent Messages", value=msg_content, inline=False)
    else:
        e.add_field(name="Messages", value="No Messages Recorded", inline=False)
    
    e.set_footer(text="Sheriff Department")
    return e

class TicketControls(View):
    def __init__(self, tid: str, ticket_owner_id: int, ticket_manager):
        super().__init__(timeout=None)
        self.tid = tid
        self.ticket_owner_id = ticket_owner_id
        self.ticket_manager = ticket_manager

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary)
    async def claim(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id == self.ticket_owner_id:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Cannot Claim",
                    description="You cannot claim your own ticket.",
                    color=Config["COLORS"]["Error"]
                ),
                ephemeral=True
            )
            return
        self.ticket_manager.claim_ticket(self.tid, interaction.user.id)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Ticket Claimed",
                description=f"Ticket claimed by {interaction.user.mention}",
                color=Config["COLORS"]["Success"]
            )
        )
        button.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: Button):
        try:
            self.ticket_manager.close_ticket(self.tid)
            for i in self.children:
                i.disabled = True
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Ticket Closed",
                    description="Preparing log...",
                    color=Config["COLORS"]["Warning"]
                )
            )
            await interaction.message.edit(view=self)

            tid_data = self.ticket_manager.tickets[self.tid]
            file_path = f"{self.tid}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(tid_data, f, indent=4, ensure_ascii=False)

            guild = interaction.guild
            log_channel = guild.get_channel(Config["CHANNELS"]["Log"])
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
                    print(f"Could not send DM to {user.name}")

            await asyncio.sleep(5)
            await interaction.channel.delete()
            os.remove(file_path)
            
        except Exception as e:
            print(f"Error closing ticket: {e}")
            traceback.print_exc()