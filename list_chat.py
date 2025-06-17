from telethon.sync import TelegramClient
from telethon.tl.types import User, Chat, Channel
from tabulate import tabulate
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
try:
    api_id = int(os.getenv("API_ID"))
    api_hash = os.getenv("API_HASH")
    if not api_id or not api_hash:
        raise ValueError("API_ID and API_HASH must be set in the .env file.")
except (ValueError, TypeError) as e:
    print(f"Error loading API credentials: {e}")
    print("Please ensure you have API_ID and API_HASH correctly set in your .env file.")
    exit()

# --- Telegram Client Initialization ---
print("Connecting to Telegram...")
try:
    client = TelegramClient('session', api_id, api_hash)
    client.start()
    print("Connection successful!")
except Exception as e:
    print(f"Failed to connect to Telegram: {e}")
    print("Please check your API_ID, API_HASH, and internet connection.")
    exit()

# --- Fetching and Categorizing Dialogs ---
print("Fetching your chat list...")
private_chats = []
groups = []
supergroups = []
channels = []
unknown_chats = []

for dialog in client.iter_dialogs():
    name = dialog.name
    chat_id = dialog.id
    username = getattr(dialog.entity, 'username', 'N/A') # Use 'N/A' if username is not present

    if isinstance(dialog.entity, User):
        private_chats.append([name, chat_id, username, 'Private'])
    elif isinstance(dialog.entity, Chat):
        groups.append([name, chat_id, username, 'Group'])
    elif isinstance(dialog.entity, Channel):
        if dialog.entity.megagroup:
            supergroups.append([name, chat_id, username, 'Supergroup'])
        else:
            channels.append([name, chat_id, username, 'Channel'])
    else:
        unknown_chats.append([name, chat_id, username, 'Unknown'])

# --- Displaying Results ---
headers = ["Name", "ID", "Username", "Type"]
table_format = "fancy_grid"

def display_section(title, data):
    if data:
        print(f"\n--- {title} ---")
        print(tabulate(data, headers=headers, tablefmt=table_format))
    else:
        print(f"\n--- {title} (None found) ---")

display_section("Private Chats", private_chats)
display_section("Groups", groups)
display_section("Supergroups", supergroups)
display_section("Channels", channels)
display_section("Unknown Chat Types", unknown_chats)

# --- Disconnect Client ---
print("\nDisconnecting from Telegram...")
client.disconnect()
print("Disconnected.")