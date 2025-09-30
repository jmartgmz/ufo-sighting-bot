"""
Channel setup and testing commands for the UFO Sighting Bot.
"""
import discord
from discord.ext import commands
import asyncio
from utils import load_config, save_config, get_random_image
from utils.auth import is_admin_user

def setup_setup_commands(bot):
    """Set up channel configuration and testing commands."""
    
    @bot.tree.command(name="setchannel", description="Set this channel for image messages")
    @discord.app_commands.checks.has_permissions(manage_guild=True)
    async def setchannel(interaction: discord.Interaction):
        config = load_config()
        guild_id = str(interaction.guild.id)
        
        # Handle both old format (integer) and new format (dictionary)
        if guild_id not in config:
            config[guild_id] = {}
        elif not isinstance(config[guild_id], dict):
            # Convert old format to new format
            config[guild_id] = {}
            
        config[guild_id]["channel_id"] = interaction.channel_id
        save_config(config)

        await interaction.response.send_message(
            f"✅ This channel (`#{interaction.channel.name}`) has been set for image messages.",
            ephemeral=True
        )

    @bot.tree.command(name="testimage", description="Send a test image that deletes after 4 seconds (Admin only)")
    async def testimage(interaction: discord.Interaction):
        # Check if user is admin
        if not is_admin_user(interaction.user.id):
            await interaction.response.send_message(
                "❌ You need admin permissions to use this command.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()

        image_url = get_random_image()
        try:
            message = await interaction.channel.send(image_url)
            await message.add_reaction("👽")
            await asyncio.sleep(4)
            await message.delete()
            await interaction.followup.send("✅ Test image sent, reacted, and deleted.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"❌ Failed: {e}", ephemeral=True)