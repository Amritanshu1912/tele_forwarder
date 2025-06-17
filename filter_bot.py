import asyncio
import os
import json
from telethon import TelegramClient, events
from dotenv import load_dotenv

# ==== Load environment variables ====
load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
keywords = ['tera']
source_chats = [-1002383316601,-1002236053558]
target_channel = -1002513293329

# ==== File to persist forwarded message IDs ====
CACHE_FILE = 'forwarded_ids.json'

def load_forwarded_ids():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_forwarded_ids(ids):
    with open(CACHE_FILE, 'w') as f:
        json.dump(list(ids), f)

forwarded_ids = load_forwarded_ids()

# ==== Connect to Telegram ====
client = TelegramClient('session', api_id, api_hash)

async def process_history(chat, target):
    async for message in client.iter_messages(chat, reverse=False):
        if message.id in forwarded_ids:
            continue
        if message.text and any(kw in message.text.lower() for kw in keywords):
            await message.forward_to(target)
            forwarded_ids.add(message.id)

@client.on(events.NewMessage(chats=source_chats))
async def handle_new(event):
    msg_id = event.message.id
    if msg_id in forwarded_ids:
        return
    text = event.message.text or ''
    if any(kw in text.lower() for kw in keywords):
        print(f"🔄 Forwarding live message: {text}")
        await event.message.forward_to(target_channel)
        forwarded_ids.add(msg_id)

async def main():
    await client.start()
    print("Resolving target channel...")
    target = await client.get_entity(target_channel)
    for chat in source_chats:
        print(f"Processing history of: {chat}")
        entity = await client.get_entity(chat)
        await process_history(entity, target)
    print("Done processing history. Now watching for new messages...")
    try:
        await client.run_until_disconnected()
    finally:
        save_forwarded_ids(forwarded_ids)

if __name__ == '__main__':
    asyncio.run(main())
