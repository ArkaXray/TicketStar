import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

Token = os.getenv('DISCORD_TOKEN')
if not Token:
    raise ValueError("Discord token not found in .env file")

Config = {
    "TOKEN": Token,
    "PREFIX": "!",
    "CATEGORY_IDS": {
        "Ozviat": int(os.getenv('CATEGORY_OZVIAT', 1546901402197041273)),
        "Shekayat": int(os.getenv('CATEGORY_SHEKAYAT', 1546901482555572264)),
        "Enteghali": int(os.getenv('CATEGORY_ENTEGHALI', 1546901558086738003)),
        "AdminFaction": int(os.getenv('CATEGORY_ADMIN', 1546901585773334668)),
        "Other": int(os.getenv('CATEGORY_OTHER', 1546901615481589890))
    },
    "ROLES": {
        "TicketSup": int(os.getenv('ROLE_TICKET_SUP', 1546258768457895986)),
        "AutoRole": int(os.getenv('ROLE_AUTO', 1546258763646767195))
    },
    "CHANNELS": {
        "TicketPanel": int(os.getenv('CHANNEL_TICKET_PANEL', 1546259071529652316)),
        "Welcome": int(os.getenv('CHANNEL_WELCOME', 1546881047440920588)),
        "Log": int(os.getenv('CHANNEL_LOG', 1546902908514205746)),
        "Voice": int(os.getenv('CHANNEL_VOICE', 1546259074876702871)),
        "Status": int(os.getenv('CHANNEL_STATUS', 1546903540528717835))
    },
    "COLORS": {
        "Primary": 0x1abc9c,
        "Success": 0x2ecc71,
        "Error": 0xe74c3c,
        "Info": 0x3498db,
        "Warning": 0xf39c12,
        "Dark": 0x2c3e50,
        "Gold": 0xf1c40f,
        "Purple": 0x9b59b6,
        "Yellow": 0xffd700,
        "Orange": 0xff8c00
    }
}