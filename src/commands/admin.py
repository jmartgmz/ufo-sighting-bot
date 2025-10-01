"""
Admin and bot information commands for the UFO Sighting Bot.
"""
import discord
from discord.ext import commands
import psutil
import platform
from datetime import datetime
from utils import (
    load_reactions, format_uptime, is_admin_user,
    add_admin_user, remove_admin_user, get_admin_users, load_config, create_welcome_embed
)

def setup_admin_commands(bot, bot_start_time):
    """Set up admin-related commands."""
    
    @bot.tree.command(name="botinfo", description="Display bot information including server count, uptime, and system stats")
    async def botinfo(interaction: discord.Interaction):
        # Check if user is admin
        if not is_admin_user(interaction.user.id):
            await interaction.response.send_message(
                "❌ You need admin permissions to use this command.",
                ephemeral=True
            )
            return
            
        # Calculate uptime
        uptime = datetime.now() - bot_start_time
        uptime_str = format_uptime(uptime)
        
        # Get system information
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
        cpu_percent = process.cpu_percent()
        
        # Get system stats
        system_memory = psutil.virtual_memory()
        system_memory_total = system_memory.total / 1024 / 1024 / 1024  # Convert to GB
        system_memory_used = system_memory.used / 1024 / 1024 / 1024    # Convert to GB
        
        # Discord bot stats
        guild_count = len(bot.guilds)
        user_count = len(bot.users)
        
        # Calculate total reactions across all servers
        reactions_data = load_reactions()
        total_reactions = 0
        total_users_with_reactions = 0
        for guild_data in reactions_data.values():
            total_reactions += sum(guild_data.values())
            total_users_with_reactions += len(guild_data)
        
        # Get Python and discord.py versions
        python_version = platform.python_version()
        discord_version = discord.__version__
        
        # Get configured channels count
        from utils import load_config
        config = load_config()
        configured_channels = len(config)
        
        # Create embed
        embed = discord.Embed(
            title="🛸 UFO Sighting Bot Information",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        # Bot Stats
        embed.add_field(
            name="📊 Bot Statistics",
            value=f"**Servers:** {guild_count}\n"
                  f"**Users:** {user_count}\n"
                  f"**Configured Channels:** {configured_channels}\n"
                  f"**Total Reactions Tracked:** {total_reactions:,}\n"
                  f"**Active Alien Spotters:** {total_users_with_reactions}",
            inline=True
        )
        
        # System Stats
        embed.add_field(
            name="💻 System Information",
            value=f"**RAM Usage:** {memory_mb:.1f} MB\n"
                  f"**CPU Usage:** {cpu_percent:.1f}%\n"
                  f"**System RAM:** {system_memory_used:.1f}/{system_memory_total:.1f} GB\n"
                  f"**Platform:** {platform.system()} {platform.release()}",
            inline=True
        )
        
        # Bot Info
        embed.add_field(
            name="🤖 Bot Details",
            value=f"**Uptime:** {uptime_str}\n"
                  f"**Python:** {python_version}\n"
                  f"**Discord.py:** {discord_version}\n"
                  f"**Latency:** {round(bot.latency * 1000)}ms",
            inline=True
        )
        
        # Guild list (if not too many)
        if guild_count <= 10:
            guild_list = "\n".join([f"• {guild.name} ({guild.member_count} members)" for guild in bot.guilds])
            embed.add_field(
                name="🏰 Servers",
                value=guild_list if guild_list else "No servers",
                inline=False
            )
        else:
            embed.add_field(
                name="🏰 Servers",
                value=f"Too many servers to list ({guild_count} total)",
                inline=False
            )
        
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="sync", description="Manually sync slash commands (Owner only)")
    async def sync_commands(interaction: discord.Interaction):
        # Check if user is admin
        if not is_admin_user(interaction.user.id):
            await interaction.response.send_message("❌ Only admins can use this command.", ephemeral=True)
            return
        
        try:
            await interaction.response.defer(ephemeral=True)
            synced = await bot.tree.sync()
            await interaction.followup.send(f"✅ Successfully synced {len(synced)} slash commands!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to sync commands: {e}", ephemeral=True)

    @bot.tree.command(name="authorize", description="Add a user to the admin list (Admin only)")
    async def authorize_user(interaction: discord.Interaction, user: discord.Member):
        # Check if user is admin
        if not is_admin_user(interaction.user.id):
            await interaction.response.send_message("❌ Only admins can manage authorized users.", ephemeral=True)
            return
        
        if add_admin_user(user.id):
            await interaction.response.send_message(
                f"✅ {user.display_name} has been added to the admin list.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"ℹ️ {user.display_name} is already an admin.",
                ephemeral=True
            )

    @bot.tree.command(name="deauthorize", description="Remove a user from the admin list (Admin only)")
    async def deauthorize_user(interaction: discord.Interaction, user: discord.Member):
        # Check if user is admin
        if not is_admin_user(interaction.user.id):
            await interaction.response.send_message("❌ Only admins can manage authorized users.", ephemeral=True)
            return
        
        if remove_admin_user(user.id):
            await interaction.response.send_message(
                f"✅ {user.display_name} has been removed from the admin list.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"ℹ️ {user.display_name} was not in the admin list.",
                ephemeral=True
            )

    @bot.tree.command(name="listauthorized", description="List all admin users (Admin only)")
    async def list_authorized(interaction: discord.Interaction):
        # Check if user is admin
        if not is_admin_user(interaction.user.id):
            await interaction.response.send_message("❌ Only admins can view the admin users list.", ephemeral=True)
            return
        
        admin_ids = get_admin_users()
        if not admin_ids:
            await interaction.response.send_message("ℹ️ No admin users are currently configured.", ephemeral=True)
            return
        
        user_list = []
        for user_id in admin_ids:
            user = bot.get_user(user_id)
            if user:
                user_list.append(f"• {user.display_name} (`{user.id}`)")
            else:
                user_list.append(f"• Unknown User (`{user_id}`)")
        
        embed = discord.Embed(
            title="� Admin Users",
            description="\n".join(user_list),
            color=0x0099ff,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Total: {len(admin_ids)} admins")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="checkreactions", description="Check reaction data persistence (Admin only)")
    async def check_reactions(interaction: discord.Interaction):
        # Check if user is admin
        if not is_admin_user(interaction.user.id):
            await interaction.response.send_message("❌ Only admins can check reaction data.", ephemeral=True)
            return
        
        reactions_data = load_reactions()
        total_reactions = sum(sum(guild_data.values()) for guild_data in reactions_data.values())
        total_guilds = len(reactions_data)
        total_users = len(set(uid for guild_data in reactions_data.values() for uid in guild_data.keys()))
        
        embed = discord.Embed(
            title="📊 Reaction Data Status",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        embed.add_field(name="Total Reactions", value=f"{total_reactions:,}", inline=True)
        embed.add_field(name="Servers with Data", value=f"{total_guilds}", inline=True)
        embed.add_field(name="Unique Users", value=f"{total_users}", inline=True)
        
        # Show some sample data
        if reactions_data:
            sample_data = []
            for guild_id, guild_data in list(reactions_data.items())[:3]:
                for user_id, count in list(guild_data.items())[:2]:
                    user = bot.get_user(int(user_id))
                    name = user.display_name if user else f"User {user_id}"
                    sample_data.append(f"• {name}: {count} reactions")
            
            if sample_data:
                embed.add_field(
                    name="Sample Data",
                    value="\n".join(sample_data[:5]) + ("..." if len(sample_data) > 5 else ""),
                    inline=False
                )
        
        embed.set_footer(text="Data loaded fresh from reactions.json")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="setlogchannel", description="Set the global logging channel for all servers (Admin only)")
    async def setlogchannel(interaction: discord.Interaction, channel: discord.TextChannel = None):
        # Check if user is admin
        if not is_admin_user(interaction.user.id):
            await interaction.response.send_message(
                "❌ You need admin permissions to set the logging channel.",
                ephemeral=True
            )
            return

        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ This command must be used in a server.",
                ephemeral=True
            )
            return

        # If no channel specified, use current channel
        if channel is None:
            channel = interaction.channel

        # Set the global log channel (logs activity from ALL servers)
        from utils import set_global_log_channel_id
        set_global_log_channel_id(channel.id)

        embed = discord.Embed(
            title="🌍 Global Logging Channel Set",
            description=f"Bot activity from **all servers** will now be sent to {channel.mention}",
            color=0x00ff41,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="📋 What gets logged:",
            value="• UFO reaction events from all servers\n• User interaction stats globally\n• Server join/leave events\n• Error notifications",
            inline=False
        )

        embed.add_field(
            name="🌐 Global Logging:",
            value="This channel will receive activity logs from every server the bot is in, not just this one.",
            inline=False
        )

        embed.add_field(
            name="ℹ️ Note:",
            value="The bot needs **Send Messages** permission in the logging channel.",
            inline=False
        )

        embed.set_footer(
            text=f"Set by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Send a test message to the logging channel
        try:
            test_embed = discord.Embed(
                title="🌍 Global Logging Channel Activated",
                description="This channel is now receiving UFO Sighting Bot activity logs **from all servers**.",
                color=0x4169E1,
                timestamp=datetime.now()
            )
            test_embed.add_field(
                name="🚀 Now tracking globally:",
                value=f"• Reactions from {len(bot.guilds)} servers\n• User activity across all servers\n• Server join/leave events",
                inline=False
            )
            test_embed.set_footer(text="UFO Sighting Bot Global Logging System")
            
            await channel.send(embed=test_embed)
        except discord.Forbidden:
            # Send error message back to user if bot can't send to log channel
            error_embed = discord.Embed(
                title="⚠️ Permission Issue",
                description=f"I cannot send messages to {channel.mention}. Please ensure I have **Send Messages** permission in that channel.",
                color=0xff6600
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @bot.tree.command(name="globalmessage", description="Send a message to all servers (Admin only)")
    async def global_message(interaction: discord.Interaction, message: str):
        # Check if user is admin
        if not is_admin_user(interaction.user.id):
            await interaction.response.send_message(
                "❌ You need admin permissions to send global messages.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        
        # Create the global message embed
        global_embed = discord.Embed(
            title="📢 Global Announcement",
            description=message,
            color=0x00ff41,
            timestamp=datetime.now()
        )
        
        global_embed.set_footer(
            text=f"Sent by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )
        
        # Get all guilds and their configured channels
        config = load_config()
        successful_sends = 0
        failed_sends = 0
        failed_guilds = []
        
        for guild in bot.guilds:
            guild_id = str(guild.id)
            
            # Try to find a configured channel for this guild
            channel_id = None
            if guild_id in config:
                guild_config = config[guild_id]
                if isinstance(guild_config, dict):
                    # New format - try log channel first, then regular channel
                    channel_id = guild_config.get("log_channel_id") or guild_config.get("channel_id")
                else:
                    # Old format - direct channel ID
                    channel_id = guild_config
            
            # If no configured channel, try to find a suitable channel
            if not channel_id:
                # Try to find a general channel or first available text channel
                for channel in guild.text_channels:
                    if channel.name.lower() in ['general', 'announcements', 'bot-commands', 'ufo']:
                        channel_id = channel.id
                        break
                
                # If still no channel found, use the first text channel the bot can send to
                if not channel_id:
                    for channel in guild.text_channels:
                        if channel.permissions_for(guild.me).send_messages:
                            channel_id = channel.id
                            break
            
            if channel_id:
                channel = bot.get_channel(channel_id)
                if channel:
                    try:
                        await channel.send(embed=global_embed)
                        successful_sends += 1
                    except discord.Forbidden:
                        failed_sends += 1
                        failed_guilds.append(f"{guild.name} (No permission)")
                    except discord.HTTPException as e:
                        failed_sends += 1
                        failed_guilds.append(f"{guild.name} (HTTP error)")
                else:
                    failed_sends += 1
                    failed_guilds.append(f"{guild.name} (Channel not found)")
            else:
                failed_sends += 1
                failed_guilds.append(f"{guild.name} (No suitable channel)")
        
        # Create summary embed
        summary_embed = discord.Embed(
            title="📊 Global Message Summary",
            color=0x00ff41 if failed_sends == 0 else 0xff6600,
            timestamp=datetime.now()
        )
        
        summary_embed.add_field(
            name="✅ Successful Sends",
            value=f"**{successful_sends}** servers",
            inline=True
        )
        
        summary_embed.add_field(
            name="❌ Failed Sends",
            value=f"**{failed_sends}** servers",
            inline=True
        )
        
        summary_embed.add_field(
            name="📈 Success Rate",
            value=f"**{(successful_sends / len(bot.guilds) * 100):.1f}%**",
            inline=True
        )
        
        summary_embed.add_field(
            name="💬 Message Sent",
            value=message[:100] + ("..." if len(message) > 100 else ""),
            inline=False
        )
        
        if failed_guilds:
            failed_list = "\n".join(failed_guilds[:10])  # Show first 10 failures
            if len(failed_guilds) > 10:
                failed_list += f"\n... and {len(failed_guilds) - 10} more"
            
            summary_embed.add_field(
                name="🔍 Failed Servers",
                value=failed_list,
                inline=False
            )
        
        summary_embed.set_footer(text="Global message delivery complete")
        
        await interaction.followup.send(embed=summary_embed, ephemeral=True)

    @bot.tree.command(name="testsetup", description="Replay the welcome setup message (Admin only)")
    async def test_setup(interaction: discord.Interaction):
        # Check if user is admin
        if not is_admin_user(interaction.user.id):
            await interaction.response.send_message(
                "❌ You need admin permissions to test the setup message.",
                ephemeral=True
            )
            return

        # Create and send the welcome embed
        welcome_embed = create_welcome_embed()
        
        await interaction.response.send_message(
            "🧪 **Testing Setup Message** - This is what new servers see when the bot joins:",
            embed=welcome_embed,
            ephemeral=True
        )