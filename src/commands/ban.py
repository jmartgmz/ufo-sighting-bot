"""
Ban management commands for the UFO Sighting Bot.
"""
import discord
from discord.ext import commands
from discord import app_commands
from src.utils.helpers import (
    is_user_banned, ban_user, unban_user, get_ban_info, load_banned_users
)
from datetime import datetime

class BanCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Ban a user from using the bot")
    @app_commands.describe(
        user="The user to ban",
        reason="Reason for the ban (optional)"
    )
    async def ban_user_command(self, interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
        """Ban a user from using the bot."""
        # Check if the user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Prevent banning administrators
        try:
            member = interaction.guild.get_member(user.id)
            if member and member.guild_permissions.administrator:
                embed = discord.Embed(
                    title="❌ Cannot Ban Administrator",
                    description="You cannot ban users with administrator permissions.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        except:
            pass  # User might not be in the server

        # Check if user is already banned
        if is_user_banned(user.id):
            embed = discord.Embed(
                title="⚠️ Already Banned",
                description=f"{user.mention} is already banned from using the bot.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Ban the user
        ban_user(user.id, reason, interaction.user.id)

        embed = discord.Embed(
            title="🔨 User Banned",
            description=f"{user.mention} has been banned from using the UFO Sighting Bot.",
            color=discord.Color.red()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Banned by", value=interaction.user.mention, inline=True)
        embed.add_field(name="Date", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=True)
        embed.set_footer(text=f"User ID: {user.id}")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unban", description="Unban a user from using the bot")
    @app_commands.describe(user="The user to unban")
    async def unban_user_command(self, interaction: discord.Interaction, user: discord.User):
        """Unban a user from using the bot."""
        # Check if the user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Check if user is banned
        if not is_user_banned(user.id):
            embed = discord.Embed(
                title="⚠️ Not Banned",
                description=f"{user.mention} is not currently banned.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Get ban info before unbanning
        ban_info = get_ban_info(user.id)
        
        # Unban the user
        if unban_user(user.id):
            embed = discord.Embed(
                title="✅ User Unbanned",
                description=f"{user.mention} has been unbanned and can now use the UFO Sighting Bot.",
                color=discord.Color.green()
            )
            embed.add_field(name="Unbanned by", value=interaction.user.mention, inline=True)
            embed.add_field(name="Date", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=True)
            
            if ban_info:
                embed.add_field(name="Original Ban Reason", value=ban_info.get("reason", "Unknown"), inline=False)
            
            embed.set_footer(text=f"User ID: {user.id}")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Unban Failed",
                description="Failed to unban the user. Please try again.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="baninfo", description="Get information about a user's ban")
    @app_commands.describe(user="The user to check ban information for")
    async def ban_info_command(self, interaction: discord.Interaction, user: discord.User):
        """Get information about a user's ban."""
        # Check if the user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        ban_info = get_ban_info(user.id)
        
        if not ban_info:
            embed = discord.Embed(
                title="ℹ️ No Ban Information",
                description=f"{user.mention} is not currently banned.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Parse the ban date
        try:
            ban_date = datetime.fromisoformat(ban_info["banned_at"])
            ban_timestamp = int(ban_date.timestamp())
        except:
            ban_timestamp = None

        embed = discord.Embed(
            title="🔍 Ban Information",
            description=f"Ban details for {user.mention}",
            color=discord.Color.red()
        )
        embed.add_field(name="Reason", value=ban_info.get("reason", "Unknown"), inline=False)
        embed.add_field(name="Banned by", value=f"<@{ban_info.get('banned_by', 'Unknown')}>", inline=True)
        
        if ban_timestamp:
            embed.add_field(name="Ban Date", value=f"<t:{ban_timestamp}:F>", inline=True)
        else:
            embed.add_field(name="Ban Date", value="Unknown", inline=True)
            
        embed.set_footer(text=f"User ID: {user.id}")
        embed.set_thumbnail(url=user.display_avatar.url)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="banlist", description="List all banned users")
    async def ban_list_command(self, interaction: discord.Interaction):
        """List all banned users."""
        # Check if the user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        banned_users = load_banned_users()
        
        if not banned_users:
            embed = discord.Embed(
                title="📋 Ban List",
                description="No users are currently banned.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="📋 Banned Users",
            description=f"Total banned users: {len(banned_users)}",
            color=discord.Color.red()
        )

        # Add up to 10 banned users to avoid embed limits
        count = 0
        for user_id, ban_info in banned_users.items():
            if count >= 10:
                embed.add_field(
                    name="...", 
                    value=f"And {len(banned_users) - 10} more banned users.", 
                    inline=False
                )
                break
                
            try:
                user = self.bot.get_user(int(user_id))
                user_name = user.display_name if user else f"Unknown User ({user_id})"
            except:
                user_name = f"Unknown User ({user_id})"
                
            reason = ban_info.get("reason", "No reason provided")
            if len(reason) > 50:
                reason = reason[:47] + "..."
                
            embed.add_field(
                name=f"{user_name}",
                value=f"**Reason:** {reason}\n**ID:** {user_id}",
                inline=True
            )
            count += 1

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(BanCommands(bot))