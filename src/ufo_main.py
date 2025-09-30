"""
UFO Sighting Bot - Main bot file.
A Discord bot that sends random UFO images and tracks user reactions.
"""
import discord
from discord.ext import commands
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Import our custom modules
from utils import load_config, load_reactions, save_reactions, get_random_image, get_random_interval, get_log_channel_id, create_welcome_embed
from commands import setup_all_commands

# Load environment variables
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="ufo ", intents=intents)

# Bot start time for uptime tracking
bot_start_time = datetime.now()

# --- Independent image loop per guild ---
async def send_images_to_guild(guild_id: str):
    """Send UFO images to a specific guild at random intervals."""
    await bot.wait_until_ready()
    while not bot.is_closed():
        config = load_config()
        if guild_id not in config:
            await asyncio.sleep(30)  # check again later
            continue

        # Handle both old format (integer) and new format (dictionary)
        guild_config = config[guild_id]
        if isinstance(guild_config, dict):
            channel_id = guild_config.get("channel_id")
        else:
            # Old format - guild_config is just the channel ID integer
            channel_id = guild_config
            
        if channel_id is None:
            await asyncio.sleep(30)
            continue

        channel = bot.get_channel(channel_id)
        if channel is None:
            await asyncio.sleep(30)
            continue

        image_url = get_random_image()
        try:
            message = await channel.send(image_url)
            await message.add_reaction("👽")
            await asyncio.sleep(4)  # how long the image stays
            await message.delete()
        except discord.HTTPException as e:
            print(f"⚠️ Failed in guild {guild_id}: {e}")

        # Each guild gets its own random interval
        interval = get_random_interval()
        await asyncio.sleep(interval)

@bot.event
async def on_ready():
    """Called when the bot is ready."""
    print(f"🤖 Bot is online as {bot.user.name}")
    
    # Set bot status to DND and activity to "watching for ufos"
    activity = discord.Activity(type=discord.ActivityType.watching, name="for Aliens")
    await bot.change_presence(status=discord.Status.dnd, activity=activity)
    
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)} commands")
        for cmd in synced:
            print(f"  - /{cmd.name}: {cmd.description}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    # Start a separate task for each guild
    for g in bot.guilds:
        bot.loop.create_task(send_images_to_guild(str(g.id)))

@bot.event
async def on_guild_join(guild):
    """Send welcome message when bot joins a new server."""
    print(f"🌟 Joined new guild: {guild.name} (ID: {guild.id})")
    
    # Create welcome embed
    welcome_embed = create_welcome_embed()
    
    # Try to find a suitable channel to send the welcome message
    # Priority: general > announcements > bot-commands > first text channel with permissions
    target_channel = None
    
    # Try common channel names first
    for channel in guild.text_channels:
        if channel.name.lower() in ['general', 'announcements', 'bot-commands', 'welcome']:
            if channel.permissions_for(guild.me).send_messages:
                target_channel = channel
                break
    
    # If no common channel found, use the first text channel we can send to
    if not target_channel:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                target_channel = channel
                break
    
    # If we found a suitable channel, send the welcome message
    if target_channel:
        try:
            await target_channel.send(embed=welcome_embed)
            print(f"✅ Sent welcome message to {guild.name} in #{target_channel.name}")
        except discord.HTTPException as e:
            print(f"❌ Failed to send welcome message to {guild.name}: {e}")
    else:
        print(f"⚠️ No suitable channel found in {guild.name} to send welcome message")

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Handle reaction tracking for UFO sightings."""
    if str(payload.emoji) != "👽":
        return
    if payload.user_id == bot.user.id:
        return

    channel = bot.get_channel(payload.channel_id)
    if channel is None:
        return

    try:
        message = await channel.fetch_message(payload.message_id)
    except Exception:
        return

    if message.author.id != bot.user.id:
        return

    user_id = str(payload.user_id)
    guild_id = str(payload.guild_id) if payload.guild_id else "dm"

    # Load current reactions data from file
    reactions_data = load_reactions()
    if guild_id not in reactions_data:
        reactions_data[guild_id] = {}
    if user_id not in reactions_data[guild_id]:
        reactions_data[guild_id][user_id] = 0

    reactions_data[guild_id][user_id] += 1
    # Save updated data back to file
    save_reactions(reactions_data)
    
    # Console log
    print(f"👽 Reaction by {user_id} in guild {guild_id}. Total: {reactions_data[guild_id][user_id]}")
    
    # Send to Discord logging channel if configured
    if payload.guild_id:  # Only for guild messages, not DMs
        log_channel_id = get_log_channel_id(payload.guild_id)
        if log_channel_id:
            log_channel = bot.get_channel(log_channel_id)
            if log_channel:
                try:
                    # Get user and guild info for better logging
                    user = bot.get_user(payload.user_id)
                    guild = bot.get_guild(payload.guild_id)
                    
                    user_name = user.display_name if user else f"User {payload.user_id}"
                    guild_name = guild.name if guild else f"Guild {payload.guild_id}"
                    
                    log_embed = discord.Embed(
                        title="👽 UFO Sighting Logged",
                        color=0x00ff41,
                        timestamp=datetime.now()
                    )
                    
                    log_embed.add_field(
                        name="👤 User",
                        value=f"**{user_name}**\n`{payload.user_id}`",
                        inline=True
                    )
                    
                    log_embed.add_field(
                        name="🏛️ Server", 
                        value=f"**{guild_name}**\n`{payload.guild_id}`",
                        inline=True
                    )
                    
                    log_embed.add_field(
                        name="📊 Total Count",
                        value=f"**{reactions_data[guild_id][user_id]}** sightings",
                        inline=True
                    )
                    
                    log_embed.add_field(
                        name="📍 Channel",
                        value=f"<#{payload.channel_id}>",
                        inline=False
                    )
                    
                    log_embed.set_footer(text="UFO Reaction Tracking System")
                    
                    await log_channel.send(embed=log_embed)
                except Exception as e:
                    # If logging fails, don't break the main functionality
                    print(f"Failed to send log to Discord channel: {e}")

# Set up all command modules
setup_all_commands(bot, bot_start_time)

if __name__ == "__main__":
    bot.run(token)