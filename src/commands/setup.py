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
            # Track this test message too so reactions count
            from ufo_main import bot_ufo_messages
            bot_ufo_messages[message.id] = str(interaction.guild.id) if interaction.guild else "dm"
            print(f"🧪 Test image sent (Message ID: {message.id}) - now tracking for reactions")
            
            await message.add_reaction("👽")
            print(f"🤖 Bot added 👽 reaction to test message {message.id}")
            await asyncio.sleep(4)
            await message.delete()
            print(f"🗑️ Test message {message.id} deleted after 4 seconds")
            await interaction.followup.send("✅ Test image sent, reacted, and deleted.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"❌ Failed: {e}", ephemeral=True)

    @bot.tree.command(name="usersightings", description="View UFO reaction counts for yourself or another user")
    @discord.app_commands.describe(
        user="The user to check sightings for (leave empty for your own sightings)"
    )
    async def usersightings(interaction: discord.Interaction, user: discord.User = None):
        from utils import load_reactions
        
        # Default to the user who ran the command
        target_user = user if user else interaction.user
        target_user_id = str(target_user.id)
        
        # Load reactions data
        reactions_data = load_reactions()
        
        # Create embed
        embed = discord.Embed(
            title=f"👽 UFO Sightings for {target_user.display_name}",
            color=0x00ff00,
            timestamp=interaction.created_at
        )
        
        # Set thumbnail to user's avatar
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        # Check if user has any sightings
        total_sightings = 0
        servers_with_sightings = 0
        sighting_details = []
        
        for guild_id, guild_data in reactions_data.items():
            if target_user_id in guild_data:
                count = guild_data[target_user_id]
                total_sightings += count
                servers_with_sightings += 1
                
                # Try to get guild name
                try:
                    guild = bot.get_guild(int(guild_id))
                    guild_name = guild.name if guild else f"Server {guild_id}"
                except:
                    guild_name = f"Server {guild_id}"
                
                sighting_details.append(f"**{guild_name}**: {count} sighting{'s' if count != 1 else ''}")
        
        if total_sightings == 0:
            embed.description = f"No UFO sightings found for {target_user.mention}.\nReact with 👽 or any emoji to UFO images to start tracking!"
            embed.color = 0x666666
        else:
            embed.description = f"Total sightings across all servers: **{total_sightings}**"
            
            # Add summary field
            embed.add_field(
                name="📊 Summary",
                value=f"🛸 **{total_sightings}** total sightings\n🏠 **{servers_with_sightings}** server{'s' if servers_with_sightings != 1 else ''}",
                inline=False
            )
            
            # Add detailed breakdown if there are sightings
            if sighting_details:
                # Split into chunks if too many servers
                details_text = "\n".join(sighting_details[:10])  # Show first 10 servers
                if len(sighting_details) > 10:
                    details_text += f"\n... and {len(sighting_details) - 10} more server{'s' if len(sighting_details) - 10 != 1 else ''}"
                
                embed.add_field(
                    name="🌍 Server Breakdown",
                    value=details_text,
                    inline=False
                )
        
        # Add footer
        if user:
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        else:
            embed.set_footer(text="Use /usersightings @user to check someone else's sightings")
        
        await interaction.response.send_message(embed=embed)