# 🕵️ Diecast Stock Watcher

A lightweight Python script to monitor product listings on diecast model websites and notify you when new items drop via Discord.

## 🔧 Features

- Scrapes multiple URLs for new product listings
- Detects and alerts only on *new* items
- Sends Discord notifications tagging a user
- Periodic monitoring with CSV-based state tracking

## ⚙️ Setup

1. **Clone this repo:**

```bash
git clone https://github.com/yourusername/diecast-stock-watcher.git
cd diecast-stock-watcher
```
2. **Install dependencies:**

```bash
pip install -r requirements.txt
```
3. **Set environment variables:**

```bash
DISCORD_WEBHOOK_URL="your_discord_webhook"
DISCORD_USER_ID="your_discord_user_id"
```
4. **Run the script:**

```bash
python watcher.py
