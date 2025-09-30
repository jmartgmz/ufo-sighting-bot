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

**User Commands:**
- `/testimage` - Send a test UFO image that deletes after 4 seconds
- `/sightingsseen` - View your alien sighting count and server leaderboard (clean embed design)
- `/globalsightings` - View your total sightings across all servers and global leaderboard (professional layout)

**Restricted Commands:**
- `/botinfo` - Display comprehensive bot information (requires authorization)

**Setup Commands:**
- `/setchannel` - Set the current channel for UFO image messages (requires Manage Server permission)

**Admin Commands:**
- `/sync` - Manually sync slash commands (admin only)
- `/authorize` - Add a user to the botinfo authorized list (admin only)
- `/deauthorize` - Remove a user from the botinfo authorized list (admin only)
- `/listauthorized` - List all users authorized for botinfo (admin only)
- `/checkreactions` - Check reaction data persistence and statistics (admin only)

### How to Use

1. Use `/setchannel` in the channel where you want UFO images to appear
2. The bot will start sending random UFO images at random intervals
3. React with 👽 to the images to track your sightings
4. Check your progress with `/sightingsseen` or `/globalsightings`

## 📁 Project Structure

```
ufo-sighting-bot/
├── src/                        # Source code
│   ├── commands/              # Command modules
│   │   ├── __init__.py       # Commands package init
│   │   ├── admin.py          # Bot info and admin commands
│   │   ├── setup.py          # Channel setup and testing
│   │   └── sightings.py      # Reaction tracking and leaderboards
│   ├── utils/                # Utility modules
│   │   ├── __init__.py       # Utils package init
│   │   ├── auth.py           # User authorization management
│   │   ├── config.py         # Configuration management
│   │   └── helpers.py        # Helper functions and constants
│   ├── ufo_main.py           # Main bot file
│   └── ufo_main_backup.py    # Backup of original monolithic file
├── data/                     # Data files (gitignored)
│   ├── config.json           # Server configurations
│   ├── reactions.json        # Reaction tracking data
│   ├── authorized_users.json # User authorization settings
│   ├── config.json.example   # Example server config
│   ├── reactions.json.example # Example reactions file
│   └── authorized_users.json.example # Example auth config
├── logs/                     # Log files
├── docs/                     # Documentation
├── run_bot.py                # Bot launcher script
├── setup.sh                  # Setup script for new installations
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🛠️ Configuration

The bot automatically creates and manages several configuration files with **persistent storage**:

- `data/config.json` - Stores channel configurations for each server
- `data/reactions.json` - Tracks user reaction counts across all servers (survives bot restarts)
- `data/authorized_users.json` - Controls who can use restricted commands

### 💾 Data Persistence

All user reaction data is automatically saved to disk and persists across bot restarts. The bot:
- ✅ Loads fresh data from files on each command
- ✅ Immediately saves changes after each reaction
- ✅ Maintains accurate counts even after crashes or restarts
- ✅ Uses file-based storage (no database required)

### 🔐 Authorization System

The bot includes a built-in authorization system for sensitive commands:

**Admin Users** - Can manage other users' permissions and use all admin commands
**Botinfo Users** - Can use the `/botinfo` command to view bot statistics

**Default Setup:**
1. On first run, the bot creates `data/authorized_users.json` with your Discord ID as an admin
2. Admins can use `/authorize @user` to grant botinfo access
3. Use `/deauthorize @user` to remove access
4. Use `/listauthorized` to see all authorized users

**Manual Configuration:**
Edit `data/authorized_users.json`:
```json
{
    "botinfo_users": [123456789012345678, 987654321098765432],
    "admin_users": [123456789012345678]
}
```

## 🏗️ Architecture

The bot follows a modular architecture for better maintainability:

### **Command Modules**
- `commands/admin.py` - Bot information and admin commands (`/botinfo`, `/sync`)
- `commands/sightings.py` - Reaction tracking and leaderboards (`/sightingsseen`, `/globalsightings`)
- `commands/setup.py` - Channel configuration and testing (`/setchannel`, `/testimage`)

### **Utility Modules**
- `utils/config.py` - Configuration file management
- `utils/helpers.py` - Helper functions and constants

### **Benefits**
- **Maintainable**: Each command category has its own file
- **Extensible**: Easy to add new command modules
- **Reusable**: Shared utilities avoid code duplication
- **Organized**: Clear separation of concerns

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.