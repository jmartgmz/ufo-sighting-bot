"""
Sighting tracking and leaderboard commands for the UFO Sighting Bot.
"""
import discord
from discord.ext import commands
from datetime import datetime
from utils import load_reactions

def setup_sightings_commands(bot):
    """Set up sighting-related commands."""
    
    @bot.tree.command(name="localsightings", description="See how many alien sightings you have reacted to in this server")
    async def localsightings(interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)

        reactions_data = load_reactions()
        guild_data = reactions_data.get(guild_id, {})
        user_count = guild_data.get(user_id, 0)

        # Calculate user's rank
        sorted_users = sorted(guild_data.items(), key=lambda item: item[1], reverse=True)
        user_rank = None
        for i, (uid, count) in enumerate(sorted_users, start=1):
            if uid == user_id:
                user_rank = i
                break

        # Get top 10 for leaderboard
        top_10 = sorted_users[:10]

        # Create embed
        embed = discord.Embed(
            title="UFO Sighting Record",
            color=0x00ff41,
            timestamp=datetime.now()
        )

        # User's personal stats
        rank_text = f"#{user_rank}" if user_rank else "Unranked"
        if user_count == 0:
            user_stats = "**No sightings yet**\nStart reacting to UFO images to track your progress"
        else:
            user_stats = f"**{user_count:,}** sightings spotted\nServer rank: **{rank_text}**"
        
        embed.add_field(
            name=f"{interaction.user.display_name}'s Sightings",
            value=user_stats,
            inline=False
        )

        # Server leaderboard
        if top_10:
            leaderboard_lines = []
            for i, (uid, count) in enumerate(top_10, start=1):
                member = interaction.guild.get_member(int(uid))
                name = member.display_name if member else "Unknown User"
                
                # Add medal emojis for top 3 only
                if i == 1:
                    emoji = "🥇"
                elif i == 2:
                    emoji = "🥈"
                elif i == 3:
                    emoji = "🥉"
                else:
                    emoji = f"{i}."
                
                # Highlight the current user
                if uid == user_id:
                    leaderboard_lines.append(f"{emoji} **{name}** - **{count:,}** sightings")
                else:
                    leaderboard_lines.append(f"{emoji} {name} - {count:,} sightings")

            embed.add_field(
                name="Server Leaderboard",
                value="\n".join(leaderboard_lines),
                inline=False
            )
        else:
            embed.add_field(
                name="Server Leaderboard",
                value="No sightings recorded yet in this server.",
                inline=False
            )

        # Server stats section
        total_server_sightings = sum(guild_data.values())
        total_users_with_sightings = len(guild_data)
        
        if total_server_sightings > 0:
            percentage = (user_count / total_server_sightings) * 100 if total_server_sightings > 0 else 0
            server_stats = (
                f"**{total_server_sightings:,}** total server sightings\n"
                f"**{total_users_with_sightings}** active users\n"
                f"You've spotted **{percentage:.1f}%** of all UFOs here"
            )
        else:
            server_stats = "Be the first to spot a UFO in this server"

        embed.add_field(
            name="Server Statistics",
            value=server_stats,
            inline=False
        )

        # Simple footer based on user count
        if user_count == 0:
            footer_msg = "Start your UFO hunting journey!"
        elif user_count < 5:
            footer_msg = "Keep watching the skies!"
        elif user_count < 10:
            footer_msg = "You're getting good at this!"
        elif user_count < 20:
            footer_msg = "You're becoming quite the UFO expert!"
        elif user_count < 50:
            footer_msg = "Impressive dedication to the truth!"
        else:
            footer_msg = "You are a true believer!"

        embed.set_footer(
            text=footer_msg,
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="globalsightings", description="See your total alien sightings across all servers")
    async def globalsightings(interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        reactions_data = load_reactions()
        
        # Add up user's counts across all guilds
        total_count = 0
        user_server_breakdown = {}
        for guild_id, guild_data in reactions_data.items():
            user_count_in_guild = guild_data.get(user_id, 0)
            if user_count_in_guild > 0:
                total_count += user_count_in_guild
                # Try to get guild name
                guild = bot.get_guild(int(guild_id))
                guild_name = guild.name if guild else f"Server {guild_id}"
                user_server_breakdown[guild_name] = user_count_in_guild

        # Build global totals for leaderboard
        global_totals = {}
        for guild_id, guild_data in reactions_data.items():
            for uid, count in guild_data.items():
                global_totals[uid] = global_totals.get(uid, 0) + count

        # Calculate user's global rank
        sorted_users = sorted(global_totals.items(), key=lambda item: item[1], reverse=True)
        user_global_rank = None
        for i, (uid, count) in enumerate(sorted_users, start=1):
            if uid == user_id:
                user_global_rank = i
                break

        # Get top 15 for global leaderboard
        top_15 = sorted_users[:15]

        # Create embed
        embed = discord.Embed(
            title="Global UFO Sighting Record",
            color=0x4169E1,
            timestamp=datetime.now()
        )

        # User's global stats
        global_rank_text = f"#{user_global_rank}" if user_global_rank else "Unranked"
        if total_count == 0:
            user_stats = "**No global sightings yet**\nExplore multiple servers to start tracking"
        else:
            user_stats = f"**{total_count:,}** total sightings across all servers\nGlobal rank: **{global_rank_text}**"
        
        embed.add_field(
            name=f"{interaction.user.display_name}'s Global Stats",
            value=user_stats,
            inline=False
        )

        # Server breakdown if user has sightings
        if user_server_breakdown:
            breakdown_lines = []
            for server_name, count in sorted(user_server_breakdown.items(), key=lambda x: x[1], reverse=True):
                breakdown_lines.append(f"**{server_name}**: {count:,} sightings")
            
            embed.add_field(
                name="Sightings by Server (Top 3)",
                value="\n".join(breakdown_lines[:3]) + ("..." if len(breakdown_lines) > 3 else ""),
                inline=False
            )

        # Global leaderboard
        if top_15:
            leaderboard_lines = []
            for i, (uid, count) in enumerate(top_15, start=1):
                # Try to get user from current guild first, then globally
                member = interaction.guild.get_member(int(uid)) if interaction.guild else None
                if member:
                    name = member.display_name
                else:
                    user_obj = bot.get_user(int(uid))
                    name = user_obj.display_name if user_obj else f"Unknown User"
                
                # Add medal emojis for top 3 only
                if i == 1:
                    emoji = "🥇"
                elif i == 2:
                    emoji = "🥈"
                elif i == 3:
                    emoji = "🥉"
                else:
                    emoji = f"{i}."
                
                # Highlight the current user
                if uid == user_id:
                    leaderboard_lines.append(f"{emoji} **{name}** - **{count:,}** sightings")
                else:
                    leaderboard_lines.append(f"{emoji} {name} - {count:,} sightings")

            embed.add_field(
                name="Global Leaderboard",
                value="\n".join(leaderboard_lines),
                inline=False
            )
        else:
            embed.add_field(
                name="Global Leaderboard",
                value="No global sightings recorded yet.",
                inline=False
            )

        # Global statistics
        total_global_sightings = sum(global_totals.values())
        total_active_users = len(global_totals)
        total_servers = len(reactions_data)
        
        if total_global_sightings > 0:
            percentage = (total_count / total_global_sightings) * 100 if total_global_sightings > 0 else 0
            global_stats = (
                f"**{total_global_sightings:,}** total global sightings\n"
                f"**{total_active_users}** active alien hunters\n"
                f"**{total_servers}** servers with activity\n"
                f"You've witnessed **{percentage:.1f}%** of all UFO encounters"
            )
        else:
            global_stats = "Be the first to discover UFOs across servers"

        embed.add_field(
            name="Global Statistics",
            value=global_stats,
            inline=False
        )

        embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed, ephemeral=True)