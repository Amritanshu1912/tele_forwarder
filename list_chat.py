from telethon.sync import TelegramClient
from telethon.tl.types import User, Chat, Channel
from tabulate import tabulate
import os
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

client = TelegramClient('session', api_id, api_hash)
client.start()

rows = []

for dialog in client.iter_dialogs():
    name = dialog.name
    chat_id = dialog.id
    username = getattr(dialog.entity, 'username', '')
    if isinstance(dialog.entity, User):
        chat_type = 'Private'
    elif isinstance(dialog.entity, Chat):
        chat_type = 'Group'
    elif isinstance(dialog.entity, Channel):
        chat_type = 'Channel' if dialog.entity.megagroup is False else 'Supergroup'
    else:
        chat_type = 'Unknown'
    rows.append([name, chat_id, username, chat_type])

headers = ["Name", "ID", "Username", "Type"]
print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
