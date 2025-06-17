# TeleForwarder: Telegram Message Filtering and Forwarding Bot

TeleForwarder is a Python-based Telegram bot designed to automatically filter messages from specified source chats (groups, channels) based on keywords and forward them to a designated target channel. It can process both historical messages and new incoming messages in real-time. The bot also includes a utility to list all your Telegram chats with their IDs, which is helpful for configuration.

## Features

- **Keyword-Based Filtering**: Forwards only messages containing specific keywords (case-insensitive).
- **Multiple Source Chats**: Monitors several source chats simultaneously.
- **Historical Scan**: Processes past messages in source chats upon the first run or when new sources are added.
- **Real-time Forwarding**: Listens for and forwards new messages as they arrive.
- **Duplicate Prevention**: Uses a local cache (`forwarded_cache.json`) to avoid forwarding the same message multiple times.
- **Rate Limit Handling**: Gracefully handles Telegram's `FloodWaitError` by waiting and retrying message sending.
- **Persistent Session**: Remembers login sessions to avoid re-authentication on every run.
- **Replit Friendly**: Includes a `keep_alive` mechanism (simple Flask server) for hosting on platforms like Replit.
- **Chat Lister Utility**: A separate script (`list_chat.py`) to easily find chat IDs required for configuration.
- **Configurable**: Uses environment variables (`.env` file) for easy setup of API credentials, keywords, and chat IDs.

## Prerequisites

- Python 3.7+
- A Telegram account
- Telegram API credentials (API ID and API Hash) obtained from my.telegram.org/apps.

## Setup

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/Amritanshu1912/tele_forwarder.git
    cd tele_forwarder
    ```

2.  **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file**:
    Create a file named `.env` in the project root. You can copy the contents from `.env.example` (see below) and fill in your details.

    ```env
    # Telegram API Credentials
    API_ID="YOUR_API_ID"
    API_HASH="YOUR_API_HASH"

    # Phone number for the bot to log in (international format, e.g., +12345678900)
    PHONE="YOUR_PHONE_NUMBER_WITH_COUNTRY_CODE"

    # Bot Configuration (for filter_bot.py)
    # Comma-separated list of keywords (case-insensitive)
    KEYWORDS="keyword1,keyword2,another keyword"

    # Comma-separated list of source chat IDs (use list_chat.py to find these)
    # Example: SOURCE_CHATS="-1001234567890,-1009876543210"
    SOURCE_CHATS=""

    # Target channel ID where messages will be forwarded (use list_chat.py to find this)
    # Example: TARGET_CHANNEL="-1001122334455"
    TARGET_CHANNEL=""
    ```

    - Replace placeholder values with your actual credentials and desired settings.
    - To get `SOURCE_CHATS` and `TARGET_CHANNEL` IDs, use the `list_chat.py` utility (see "Running the Bot" section).

## Configuration (Environment Variables in `.env`)

- `API_ID`: Your Telegram application API ID.
- `API_HASH`: Your Telegram application API Hash.
- `PHONE`: Your Telegram phone number (used by `filter_bot.py` for the initial login).
- `KEYWORDS`: A comma-separated list of keywords. Messages containing any of these keywords will be forwarded.
- `SOURCE_CHATS`: A comma-separated list of chat IDs (integers). These are the chats the bot will monitor.
- `TARGET_CHANNEL`: The ID (integer) of the channel where filtered messages will be sent.

## Running the Bot

### 1. Chat Lister Utility (`list_chat.py`)

This script helps you find the IDs for your `SOURCE_CHATS` and `TARGET_CHANNEL`.

```bash
python list_chat.py
```

On the first run, it might ask for your phone number and a login code sent to your Telegram account if a `session.session` file doesn't exist or is invalid. It will then display a list of all your chats, groups, and channels with their respective IDs.

### 2. Main Forwarder Bot (`filter_bot.py`)

This is the main bot that filters and forwards messages.

```bash
python filter_bot.py
```

On the first run, it will ask for your phone number (if not already authenticated via `telegram_session.session`) and a login code sent to your Telegram account. Subsequent runs will use the saved session.

The bot will:

- Scan historical messages in `SOURCE_CHATS`.
- Listen for new messages in `SOURCE_CHATS`.
- Forward matching messages to `TARGET_CHANNEL`.
- If running on a platform like Replit, the `keep_alive` web server will start to prevent the bot from sleeping.

## How it Works

- **`filter_bot.py`**:

  1.  Connects to Telegram using your API credentials and phone number.
  2.  Loads configuration (keywords, source/target chats) from the `.env` file.
  3.  Loads a cache of already forwarded message IDs from `forwarded_cache.json` to prevent duplicates.
  4.  Scans the message history of all `SOURCE_CHATS` for messages containing any of the `KEYWORDS`.
  5.  Formats and forwards matching historical messages to the `TARGET_CHANNEL`, adding a unique, sequential number (e.g., `#0001`) to each.
  6.  Continuously listens for new messages in `SOURCE_CHATS`.
  7.  If a new message matches the keywords, it's formatted and forwarded.
  8.  Message IDs are added to the cache after successful forwarding. The cache is saved periodically and on exit/crash.
  9.  The `keep_alive.py` script runs a simple Flask web server, which is useful for platforms like Replit that might stop idle processes.

- **`list_chat.py`**:
  1.  Connects to Telegram using `API_ID` and `API_HASH` from `.env`.
  2.  Iterates through all your dialogs (chats).
  3.  Categorizes them (Private Chats, Groups, Supergroups, Channels) and displays them in a table with their Name, ID, and Username.

## File Structure

```
tele_forwarder/
├── .env                # (You create this) Stores API credentials and configuration
├── .env.example        # Example environment file
├── .gitignore          # Specifies intentionally untracked files
├── filter_bot.py       # Main bot script for filtering and forwarding
├── keep_alive.py       # Flask server for Replit hosting
├── list_chat.py        # Utility to list chat IDs
├── requirements.txt    # Python dependencies
├── forwarded_cache.json # (Generated by bot) Caches forwarded message IDs
├── telegram_session.session # (Generated by filter_bot.py) Stores its session data
└── session.session     # (Generated by list_chat.py) Stores its session data
```

## Troubleshooting

- **Authentication Issues**: Ensure `API_ID`, `API_HASH`, and `PHONE` in your `.env` file are correct. You might need to delete the `.session` files (`telegram_session.session`, `session.session`) to force a re-login.
- **Chat Not Found / Invalid Peer**: Double-check the chat IDs in `SOURCE_CHATS` and `TARGET_CHANNEL`. Ensure the bot account is a member of these chats/channels and has permission to read/send messages.
- **No Messages Forwarded**:
  - Verify `KEYWORDS` are correctly set and present in the messages.
  - Ensure `SOURCE_CHATS` and `TARGET_CHANNEL` are correct.
  - Check the bot's console output for any error messages.

## Contributing

Contributions, issues, and feature requests are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is open-source. Please refer to the repository for specific licensing information if available. (Assuming no explicit license file, otherwise, refer to it).

```

```
