# 🛸 UFO Sighting Bot

This bot randomly sends UFO images to configured channels and tracks user reactions.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A Discord application and bot token

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ufo-sighting-bot.git
   cd ufo-sighting-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Discord bot token
   ```

4. **Run the bot**
   ```bash
   python run_bot.py
   ```
   
   Or run directly from the src directory:
   ```bash
   python src/ufo_main.py
   ```

### Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the bot token and add it to your `.env` file
5. Go to "OAuth2" > "URL Generator"
6. Select scopes: `bot`, `applications.commands`
7. Select permissions: `Send Messages`, `Add Reactions`, `Manage Messages`, `Use Slash Commands`
8. Invite the bot to your server using the generated URL

## 🎮 Commands

### Slash Commands

- `/setchannel` - Set the current channel for UFO image messages (requires Manage Server permission)
- `/testimage` - Send a test UFO image that deletes after 4 seconds
- `/sightingsseen` - View your alien sighting count and server leaderboard
- `/globalsightings` - View your total sightings across all servers and global leaderboard

### How to Use

1. Use `/setchannel` in the channel where you want UFO images to appear
2. The bot will start sending random UFO images at random intervals
3. React with 👽 to the images to track your sightings
4. Check your progress with `/sightingsseen` or `/globalsightings`

## 📁 Project Structure

```
ufo-sighting-bot/
├── src/                 # Source code
│   └── ufo_main.py     # Main bot file
├── data/               # Data files (gitignored)
│   ├── config.json     # Server configurations
│   ├── reactions.json  # Reaction tracking data
│   ├── config.json.example     # Example server config
│   └── reactions.json.example  # Example reactions file
├── docs/               # Documentation
├── run_bot.py          # Bot launcher script
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## 🛠️ Configuration

The bot automatically creates and manages two configuration files:

- `data/config.json` - Stores channel configurations for each server
- `data/reactions.json` - Tracks user reaction counts across all servers

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.