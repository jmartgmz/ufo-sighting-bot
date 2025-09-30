import discord
from discord.ext import commands
import asyncio
import random
import os
import json
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="ufo ", intents=intents)

CONFIG_FILE = "data/config.json"
REACTIONS_FILE = "data/reactions.json"

# --- File handling ---
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def load_reactions():
    if not os.path.exists(REACTIONS_FILE):
        return {}
    with open(REACTIONS_FILE, "r") as f:
        return json.load(f)

def save_reactions(data):
    with open(REACTIONS_FILE, "w") as f:
        json.dump(data, f, indent=4)

IMAGE_URLS = [
    "https://s.hdnux.com/photos/01/25/20/06/22348185/4/rawImage.jpg",
    "https://brobible.com/wp-content/uploads/2023/08/ufo-over-city-clouds.png",
    "https://api.time.com/wp-content/uploads/2016/02/150222-ufo-sightings-06.jpg",
    "https://www.washingtonpost.com/news/morning-mix/wp-content/uploads/sites/21/2015/01/UFO-04-1024x666.jpg",
    "https://hips.hearstapps.com/hmg-prod/images/vintage-old-black-and-white-ufo-photo-royalty-free-image-1677115000.jpg?resize=1200:*",
    "https://api.time.com/wp-content/uploads/2016/02/150222-ufo-sightings-06.jpg",
]

reactions_data = load_reactions()

# --- Independent image loop per guild ---
async def send_images_to_guild(guild_id: str):
    await bot.wait_until_ready()
    while not bot.is_closed():
        config = load_config()
        if guild_id not in config:
            await asyncio.sleep(30)  # check again later
            continue

        channel = bot.get_channel(config[guild_id])
        if channel is None:
            await asyncio.sleep(30)
            continue

        image_url = random.choice(IMAGE_URLS)
        try:
            message = await channel.send(image_url)
            await message.add_reaction("👽")
            await asyncio.sleep(4)  # how long the image stays
            await message.delete()
        except discord.HTTPException as e:
            print(f"⚠️ Failed in guild {guild_id}: {e}")

        # Each guild gets its own random interval
        INTERVALS = [20 * 60, 30 * 60, 2 * 60 * 60, 1 * 60 * 60]  # in seconds
        interval = random.choice(INTERVALS)
        await asyncio.sleep(interval)

@bot.event
async def on_ready():
    print(f"🤖 Bot is online as {bot.user.name}")
    await bot.tree.sync()
    print("Slash commands synced")

    # Start a separate task for each guild
    for g in bot.guilds:
        bot.loop.create_task(send_images_to_guild(str(g.id)))

# --- Slash commands ---
@bot.tree.command(name="setchannel", description="Set this channel for image messages")
@discord.app_commands.checks.has_permissions(manage_guild=True)
async def setchannel(interaction: discord.Interaction):
    config = load_config()
    guild_id = str(interaction.guild.id)
    config[guild_id] = interaction.channel_id
    save_config(config)

    await interaction.response.send_message(
        f"✅ This channel (`#{interaction.channel.name}`) has been set for image messages.",
        ephemeral=True
    )

@bot.tree.command(name="testimage", description="Send a test image that deletes after 4 seconds")
async def testimage(interaction: discord.Interaction):
    await interaction.response.defer()

    image_url = random.choice(IMAGE_URLS)
    try:
        message = await interaction.channel.send(image_url)
        await message.add_reaction("👽")
        await asyncio.sleep(4)
        await message.delete()
        await interaction.followup.send("✅ Test image sent, reacted, and deleted.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"❌ Failed: {e}", ephemeral=True)

# --- Reaction tracking ---
@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
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

    if guild_id not in reactions_data:
        reactions_data[guild_id] = {}
    if user_id not in reactions_data[guild_id]:
        reactions_data[guild_id][user_id] = 0

    reactions_data[guild_id][user_id] += 1
    save_reactions(reactions_data)
    print(f"👽 Reaction by {user_id} in guild {guild_id}. Total: {reactions_data[guild_id][user_id]}")

@bot.tree.command(name="sightingsseen", description="See how many alien sightings you have reacted to")
async def sightingsseen(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
        return

    guild_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)

    guild_data = reactions_data.get(guild_id, {})
    user_count = guild_data.get(user_id, 0)

    sorted_users = sorted(guild_data.items(), key=lambda item: item[1], reverse=True)
    top_5 = sorted_users[:5]

    leaderboard_lines = []
    for i, (uid, count) in enumerate(top_5, start=1):
        member = interaction.guild.get_member(int(uid))
        name = member.name if member else f"User ID {uid}"
        leaderboard_lines.append(f"{i}. **{name}**: {count}")

    leaderboard_text = "\n".join(leaderboard_lines) if leaderboard_lines else "No reactions yet."

    await interaction.response.send_message(
        f"You have reacted with 👽 **{user_count}** times.\n\n"
        f"🏆 Top alien sightings in this server:\n{leaderboard_text}",
        ephemeral=True
    )

@bot.tree.command(name="globalsightings", description="See your total alien sightings across all servers")
async def globalsightings(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    # Add up counts across all guilds
    total_count = 0
    for guild_id, guild_data in reactions_data.items():
        total_count += guild_data.get(user_id, 0)

    # Build global totals
    global_totals = {}
    for guild_id, guild_data in reactions_data.items():
        for uid, count in guild_data.items():
            global_totals[uid] = global_totals.get(uid, 0) + count

    sorted_users = sorted(global_totals.items(), key=lambda item: item[1], reverse=True)
    top_50 = sorted_users[:50]

    leaderboard_lines = []
    for i, (uid, count) in enumerate(top_50, start=1):
        member = interaction.guild.get_member(int(uid))
        if member:
            name = member.name
        else:
            user_obj = bot.get_user(int(uid))
            name = user_obj.name if user_obj else f"User ID {uid}"
        leaderboard_lines.append(f"{i}. **{name}**: {count}")


    leaderboard_text = "\n".join(leaderboard_lines) if leaderboard_lines else "No reactions yet."

    await interaction.response.send_message(
        f"You have reacted with 👽 **{total_count}** times across all servers.\n\n"
        f"🌍 Global top alien spotters:\n{leaderboard_text}",
        ephemeral=True
    )

bot.run(token)