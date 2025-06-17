# main_bot.py

import asyncio
import os
import json
import logging
from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import FloodWaitError
from dotenv import load_dotenv
import atexit
from keep_alive import keep_alive  # Import the keep_alive function for Replit hosting

# === Configuration ===
# Load environment variables from a .env file
load_dotenv()

# Set up basic logging
# This will output logs with a timestamp, log level, and message.
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- User-defined settings ---
# Your Telegram API credentials from my.telegram.org
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# List of keywords to search for (case-insensitive)
KEYWORDS = ['tera']

# List of source chat IDs (can be channel/group IDs)
SOURCE_CHATS = [-1002383316601, -1002236053558]

# The target channel ID where messages will be sent
TARGET_CHANNEL = -1002513293329

# --- System settings ---
# File for caching sent message IDs and the counter to avoid duplicates
CACHE_FILE = 'forwarded_cache.json'


# === Cache Management ===
def load_cache():
    """Loads forwarded message IDs and the message counter from the cache file."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                logging.info(
                    f"Cache loaded: {len(data.get('ids', []))} IDs found, counter at {data.get('counter', 1)}."
                )
                return set(data.get('ids', [])), data.get('counter', 1)
        except json.JSONDecodeError:
            logging.warning("Cache file is corrupted. Starting fresh.")
            return set(), 1
    return set(), 1


def save_cache(ids, counter):
    """Saves the given IDs and counter to the cache file."""
    logging.info(f"Writing {len(ids)} IDs and counter {counter} to cache...")
    with open(CACHE_FILE, 'w') as f:
        json.dump({'ids': list(ids), 'counter': counter}, f, indent=4)
    logging.info("Cache file written successfully.")


# === Initialization ===
# Initialize the Telegram client
# Using a file-based session to remember the login
client = TelegramClient('telegram_session', int(API_ID), API_HASH)

# Load cache at startup
forwarded_ids, message_count = load_cache()

# Register the save_cache function to be called on script exit
atexit.register(lambda: save_cache(forwarded_ids, message_count))


# === Core Functions ===
def format_message(index, content):
    """Formats the message with a zero-padded index number."""
    return f"#{str(index).zfill(4)}\n\n{content}"


async def send_message_safely(peer, message_text):
    """
    Sends a message and handles FloodWaitError by waiting and retrying.
    This is the key to making the script "fail-proof".
    """
    while True:
        try:
            await client.send_message(peer, message_text)
            break  # Break the loop if the message was sent successfully
        except FloodWaitError as e:
            logging.warning(
                f"Flood wait error. Waiting for {e.seconds} seconds before retrying."
            )
            await asyncio.sleep(
                e.seconds + 5)  # Wait for the specified time + a small buffer
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while sending message: {e}")
            break  # Exit on other errors to avoid infinite loops


async def process_history(chat_id, target_entity):
    """Scans the historical messages of a chat for keywords."""
    global message_count
    logging.info(f"Scanning message history for chat: {chat_id}")

    try:
        chat_entity = await client.get_entity(chat_id)
        async for message in client.iter_messages(
                chat_entity, limit=None):  # Use limit=None to get all history
            if message.id in forwarded_ids:
                continue  # Skip already processed messages

            if message.text and any(kw.lower() in message.text.lower()
                                    for kw in KEYWORDS):
                formatted = format_message(message_count, message.text)
                await send_message_safely(target_entity, formatted)

                forwarded_ids.add(message.id)
                logging.info(
                    f"[History] Forwarded message #{message_count} from chat {chat_id}"
                )
                message_count += 1

    except Exception as e:
        logging.error(f"Failed to process history for chat {chat_id}: {e}")


# === Event Handler for New Messages ===
@client.on(events.NewMessage(chats=SOURCE_CHATS))
async def handle_new_message(event):
    """Handles new incoming messages in the source chats."""
    global message_count
    message = event.message

    if message.id in forwarded_ids:
        logging.info(f"Received duplicate message {message.id}, skipping.")
        return

    text = message.text or ''
    if any(kw.lower() in text.lower() for kw in KEYWORDS):
        formatted = format_message(message_count, text)
        await send_message_safely(TARGET_CHANNEL, formatted)

        forwarded_ids.add(message.id)
        logging.info(
            f"[Live] Forwarded new message #{message_count} from chat {event.chat_id}"
        )
        message_count += 1


# === Main Execution Logic ===
async def main():
    """The main function to start the bot."""
    # Start the web server to keep the Repl alive
    keep_alive()

    await client.start(
        phone=os.getenv("PHONE")
    )  # You might need to provide a phone number on first run
    logging.info("Client connected to Telegram.")

    # Get the target channel entity
    target = await client.get_entity(TARGET_CHANNEL)

    # First, scan the history of all source chats
    logging.info("Starting historical scan...")
    for chat in SOURCE_CHATS:
        await process_history(chat, target)

    logging.info("Historical scan complete. Now watching for new messages...")

    # Manually save cache after the historical scan is done
    save_cache(forwarded_ids, message_count)

    # This will run forever, listening for new messages
    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"The bot has crashed: {e}")
    finally:
        # Final attempt to save cache upon a crash
        save_cache(forwarded_ids, message_count)
        logging.info("Bot shutting down. Cache saved.")
