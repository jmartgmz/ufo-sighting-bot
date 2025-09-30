"""
Helper utilities and constants for the UFO Sighting Bot.
"""
import random
import discord
from datetime import datetime

# UFO image URLs
IMAGE_URLS = [
    "https://s.hdnux.com/photos/01/25/20/06/22348185/4/rawImage.jpg",
    "https://brobible.com/wp-content/uploads/2023/08/ufo-over-city-clouds.png",
    "https://api.time.com/wp-content/uploads/2016/02/150222-ufo-sightings-06.jpg",
    "https://www.washingtonpost.com/news/morning-mix/wp-content/uploads/sites/21/2015/01/UFO-04-1024x666.jpg",
    "https://hips.hearstapps.com/hmg-prod/images/vintage-old-black-and-white-ufo-photo-royalty-free-image-1677115000.jpg?resize=1200:*",
    "https://api.time.com/wp-content/uploads/2016/02/150222-ufo-sightings-06.jpg",
]

# Random intervals for image posting (in seconds)
INTERVALS = [20 * 60, 30 * 60, 2 * 60 * 60, 1 * 60 * 60]  # 20m, 30m, 2h, 1h

def get_random_image():
    """Get a random UFO image URL."""
    return random.choice(IMAGE_URLS)

def get_random_interval():
    """Get a random interval for image posting."""
    return random.choice(INTERVALS)

def format_uptime(uptime_delta):
    """Format a timedelta object into a readable uptime string."""
    days = uptime_delta.days
    hours = uptime_delta.seconds // 3600
    minutes = (uptime_delta.seconds // 60) % 60
    seconds = uptime_delta.seconds % 60
    return f"{days}d {hours}h {minutes}m {seconds}s"

def create_welcome_embed():
    """Create the welcome message embed for new servers."""
    embed = discord.Embed(
        title="🛸 Welcome to UFO Sighting Bot!",
        description="Thanks for adding me to your server! Let's get you set up to start tracking alien encounters.",
        color=0x00ff41,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="🚀 Quick Setup",
        value="To get started, an admin needs to run `/setchannel` in the channel where you want UFO images to appear.",
        inline=False
    )
    
    embed.add_field(
        name="📋 What I Do",
        value="• Send random UFO images at random intervals\n"
              "• Track 👽 reactions as \"sightings\"\n"
              "• Provide leaderboards for top alien spotters\n"
              "• Offer admin tools for bot management",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Essential Commands",
        value="**Setup:**\n"
              "`/setchannel` - Set the UFO images channel\n"
              "`/help` - View all available commands\n\n"
              "**For Users:**\n"
              "`/localsightings` - Server leaderboard\n"
              "`/globalsightings` - Global leaderboard\n"
              "`/support` - Get help or report issues",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Admin Features",
        value="Admins can access additional commands like `/botinfo`, `/setlogchannel`, and more. Use `/helpadmin` to see all admin commands.",
        inline=False
    )
    
    embed.add_field(
        name="🎯 How It Works",
        value="1. Set a channel with `/setchannel`\n"
              "2. I'll start posting UFO images randomly\n"
              "3. Users react with 👽 to log sightings\n"
              "4. Check leaderboards to see top spotters!",
        inline=False
    )
    
    embed.set_footer(
        text="Need help? Use /support or /help • Ready to start? Use /setchannel!",
        icon_url="https://cdn.discordapp.com/emojis/1234567890123456789.png"  # UFO emoji if available
    )
    
    return embed