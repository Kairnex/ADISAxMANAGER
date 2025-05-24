# EditGuard Telegram Bot

A Telegram bot to delete edited messages from unauthorized users in groups, warn them, and mute after 3 warnings.

## Features
- Deletes edited messages
- Warns users and tracks warnings in MongoDB
- Mutes after 3 warnings for 10 minutes
- Admin buttons to remove warnings
- Authorization system with /auth, /unauth, /authlist
- Sudo-only broadcast and maintenance
- Pretty start/help UI with support/channel buttons

## Setup
1. Clone the repo
2. Copy `.env.example` to `.env` and add your credentials
3. Run `pip install -r requirements.txt`
4. Start the bot: `python main.py`

## Hosting
Works on VPS or with webhook setups on Heroku/GCP/etc.

## Author
Your Name | [@YourUsername](https://t.me/YourUsername)
