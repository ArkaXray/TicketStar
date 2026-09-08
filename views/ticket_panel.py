import discord
from discord.ui import View, Button, Modal, TextInput, Select
from config import Config
import traceback

class TicketModal(Modal):
    def __init__(self, ticket_type: str):
        super().__init__(title=f"Create {ticket_type} Ticket")
        self.ticket_type = ticket_type
        self.add_item(TextInput(
            label="Title",
            style=discord.TextStyle.short,
            placeholder="Enter a descriptive title for your ticket...",
            max_length=100,
            required=True
        ))
        self.add_item(TextInput(
            label="Description",
            style=discord.TextStyle.paragraph,
            placeholder="Please explain your issue in detail...",
            max_length=1000,
            required=True
        ))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            title = self.children[0].value
            reason = self.children[1].value
            from cogs.ticket_system import create_ticket_channel
            await create_ticket_channel(interaction, self.ticket_type, title, reason)
        except Exception as e:
            print(f"Error in TicketModal: {e}")
            traceback.print_exc()
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error",
                    description=f"An error occurred:\n{str(e)}",
                    color=Config["COLORS"]["Error"]
                ),
                ephemeral=True
            )

class TicketPanel(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        # Add select menu using decorator
        # Select is defined below with @discord.ui.select
        
        # Add link button manually (this works with url)
        link_button = Button(
            label="Sheriff Department Website",
            style=discord.ButtonStyle.link,
            url="https://starcityroleplay.com"
        )
        self.add_item(link_button)

    @discord.ui.select(
        placeholder="Select Ticket Type...",
        options=[
            discord.SelectOption(
                label="Ozviat",
                description="New Membership Request",
                value="Ozviat"
            ),
            discord.SelectOption(
                label="Shekayat",
                description="Register a Complaint",
                value="Shekayat"
            ),
            discord.SelectOption(
                label="Enteghali",
                description="Transfer Request",
                value="Enteghali"
            ),
            discord.SelectOption(
                label="Chief Of Sheriff",
                description="Chief Related Matters",
                value="Chief Of Sheriff"
            ),
            discord.SelectOption(
                label="Other",
                description="Other Inquiries",
                value="Other"
            )
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: Select):
        ticket_type = select.values[0]
        await interaction.response.send_modal(TicketModal(ticket_type))