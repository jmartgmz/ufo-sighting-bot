"""
Support system commands for the UFO Sighting Bot.
Allows users to send support requests to admins and receive replies.
"""
import discord
from datetime import datetime
import uuid
from utils.auth import is_admin_user
from utils.config import load_config, save_config

def setup_support_commands(bot):
    """Set up support-related commands."""
    
    @bot.tree.command(name="support", description="Send a support request to the bot administrators")
    async def support_request(interaction: discord.Interaction, message: str):
        # Generate unique ticket ID
        ticket_id = str(uuid.uuid4())[:8]
        
        # Load config to find support channel
        config = load_config()
        support_channel_id = None
        
        # Look for any guild with a support_channel_id configured
        for guild_config in config.values():
            if isinstance(guild_config, dict) and "support_channel_id" in guild_config:
                support_channel_id = guild_config["support_channel_id"]
                break
        
        if not support_channel_id:
            await interaction.response.send_message(
                "❌ No support channel has been configured. Please contact an administrator.",
                ephemeral=True
            )
            return
        
        support_channel = bot.get_channel(support_channel_id)
        if not support_channel:
            await interaction.response.send_message(
                "❌ Support channel not found. Please contact an administrator.",
                ephemeral=True
            )
            return
        
        # Store the support ticket
        if "support_tickets" not in config:
            config["support_tickets"] = {}
        
        config["support_tickets"][ticket_id] = {
            "user_id": interaction.user.id,
            "user_name": interaction.user.display_name,
            "guild_id": interaction.guild.id if interaction.guild else None,
            "guild_name": interaction.guild.name if interaction.guild else "Direct Message",
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "status": "open"
        }
        save_config(config)
        
        # Create embed for support channel
        support_embed = discord.Embed(
            title="🎫 New Support Request",
            color=0xff6600,
            timestamp=datetime.now()
        )
        
        support_embed.add_field(
            name="📋 Ticket ID",
            value=f"`{ticket_id}`",
            inline=True
        )
        
        support_embed.add_field(
            name="👤 User",
            value=f"**{interaction.user.display_name}**\n`{interaction.user.id}`",
            inline=True
        )
        
        support_embed.add_field(
            name="🏛️ Server",
            value=interaction.guild.name if interaction.guild else "Direct Message",
            inline=True
        )
        
        support_embed.add_field(
            name="💬 Message",
            value=message,
            inline=False
        )
        
        support_embed.add_field(
            name="📝 Reply Instructions",
            value=f"Use `/reply {ticket_id} <your response>` to respond to this ticket.",
            inline=False
        )
        
        support_embed.set_footer(text="UFO Sighting Bot Support System")
        
        try:
            await support_channel.send(embed=support_embed)
            
            # Confirm to user
            user_embed = discord.Embed(
                title="✅ Support Request Sent",
                description=f"Your support request has been sent to the administrators.",
                color=0x00ff41,
                timestamp=datetime.now()
            )
            
            user_embed.add_field(
                name="🎫 Ticket ID",
                value=f"`{ticket_id}`",
                inline=True
            )
            
            user_embed.add_field(
                name="⏰ Status",
                value="Open - Awaiting Response",
                inline=True
            )
            
            user_embed.add_field(
                name="💬 Your Message",
                value=message,
                inline=False
            )
            
            user_embed.set_footer(text="You will receive a DM when an admin responds")
            
            await interaction.response.send_message(embed=user_embed, ephemeral=True)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Unable to send support request. The bot may not have permission to send messages to the support channel.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred while sending your support request: {str(e)}",
                ephemeral=True
            )

    @bot.tree.command(name="supportchannel", description="Set the channel to receive support requests (Admin only)")
    async def set_support_channel(interaction: discord.Interaction, channel: discord.TextChannel = None):
        # Check if user is admin
        if not is_admin_user(interaction.user.id):
            await interaction.response.send_message(
                "❌ You need admin permissions to set the support channel.",
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

        guild_id = str(interaction.guild.id)
        
        # Load config and update support channel
        config = load_config()
        
        if guild_id not in config:
            config[guild_id] = {}
        elif not isinstance(config[guild_id], dict):
            # Convert old format to new format
            old_value = config[guild_id]
            config[guild_id] = {"channel_id": old_value}
        
        config[guild_id]["support_channel_id"] = channel.id
        save_config(config)

        embed = discord.Embed(
            title="🎫 Support Channel Set",
            description=f"Support requests will now be sent to {channel.mention}",
            color=0x00ff41,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="📋 What gets sent here:",
            value="• User support requests\n• Ticket IDs for replies\n• User and server information\n• Timestamps",
            inline=False
        )

        embed.add_field(
            name="📝 How to reply:",
            value="Use `/reply <ticket_id> <your response>` to respond to support tickets.",
            inline=False
        )

        embed.add_field(
            name="ℹ️ Note:",
            value="The bot needs **Send Messages** permission in the support channel.",
            inline=False
        )

        embed.set_footer(
            text=f"Set by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Send a test message to the support channel
        try:
            test_embed = discord.Embed(
                title="🎫 Support Channel Activated",
                description="This channel is now receiving UFO Sighting Bot support requests.",
                color=0x4169E1,
                timestamp=datetime.now()
            )
            test_embed.add_field(
                name="🚀 Ready to help users with:",
                value="Bug reports, feature requests, questions, and more!",
                inline=False
            )
            test_embed.set_footer(text="UFO Sighting Bot Support System")
            
            await channel.send(embed=test_embed)
        except discord.Forbidden:
            # Send error message back to user if bot can't send to support channel
            error_embed = discord.Embed(
                title="⚠️ Permission Issue",
                description=f"I cannot send messages to {channel.mention}. Please ensure I have **Send Messages** permission in that channel.",
                color=0xff6600
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @bot.tree.command(name="reply", description="Reply to a support ticket (Admin only)")
    async def reply_to_ticket(interaction: discord.Interaction, ticket_id: str, response: str):
        # Check if user is admin
        if not is_admin_user(interaction.user.id):
            await interaction.response.send_message(
                "❌ You need admin permissions to reply to support tickets.",
                ephemeral=True
            )
            return
        
        # Load config and find the ticket
        config = load_config()
        tickets = config.get("support_tickets", {})
        
        if ticket_id not in tickets:
            await interaction.response.send_message(
                f"❌ Ticket `{ticket_id}` not found. Please check the ticket ID.",
                ephemeral=True
            )
            return
        
        ticket = tickets[ticket_id]
        user_id = ticket["user_id"]
        
        # Get the user to send DM
        user = bot.get_user(user_id)
        if not user:
            await interaction.response.send_message(
                f"❌ Could not find user for ticket `{ticket_id}`. They may have left Discord or blocked the bot.",
                ephemeral=True
            )
            return
        
        # Create response embed for user
        user_embed = discord.Embed(
            title="📬 Support Response Received",
            color=0x00ff41,
            timestamp=datetime.now()
        )
        
        user_embed.add_field(
            name="🎫 Ticket ID",
            value=f"`{ticket_id}`",
            inline=True
        )
        
        user_embed.add_field(
            name="📅 Original Request",
            value=ticket["timestamp"][:10],  # Just the date
            inline=True
        )
        
        user_embed.add_field(
            name="💬 Your Original Message",
            value=ticket["message"],
            inline=False
        )
        
        user_embed.add_field(
            name="📝 Admin Response",
            value=response,
            inline=False
        )
        
        user_embed.add_field(
            name="🔄 Need More Help?",
            value="Use `/support <message>` to create a new support request if you need further assistance.",
            inline=False
        )
        
        user_embed.set_footer(text=f"Responded by {interaction.user.display_name}")
        
        try:
            await user.send(embed=user_embed)
            
            # Update ticket status
            tickets[ticket_id]["status"] = "closed"
            tickets[ticket_id]["admin_response"] = response
            tickets[ticket_id]["admin_responder"] = interaction.user.display_name
            tickets[ticket_id]["response_timestamp"] = datetime.now().isoformat()
            save_config(config)
            
            # Confirm to admin
            admin_embed = discord.Embed(
                title="✅ Reply Sent Successfully",
                description=f"Your response has been sent to **{ticket['user_name']}** via DM.",
                color=0x00ff41,
                timestamp=datetime.now()
            )
            
            admin_embed.add_field(
                name="🎫 Ticket ID",
                value=f"`{ticket_id}`",
                inline=True
            )
            
            admin_embed.add_field(
                name="👤 User",
                value=f"**{ticket['user_name']}**",
                inline=True
            )
            
            admin_embed.add_field(
                name="📝 Your Response",
                value=response,
                inline=False
            )
            
            admin_embed.set_footer(text="Ticket has been marked as closed")
            
            await interaction.response.send_message(embed=admin_embed, ephemeral=True)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                f"❌ Could not send DM to **{ticket['user_name']}**. They may have DMs disabled or have blocked the bot.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred while sending the reply: {str(e)}",
                ephemeral=True
            )