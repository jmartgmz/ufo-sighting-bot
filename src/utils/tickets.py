"""
Ticket management utilities for the UFO Sighting Bot.
Handles loading, saving, and managing support tickets.
"""
import json
import os
from datetime import datetime

# File path for tickets data
TICKETS_FILE = "data/tickets.json"

def load_tickets():
    """Load support tickets from JSON file."""
    if not os.path.exists(TICKETS_FILE):
        return {}
    try:
        with open(TICKETS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_tickets(tickets_data):
    """Save support tickets to JSON file."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(TICKETS_FILE), exist_ok=True)
    with open(TICKETS_FILE, "w") as f:
        json.dump(tickets_data, f, indent=4)

def create_ticket(user_id, user_name, guild_id, guild_name, message):
    """Create a new support ticket and return the ticket ID."""
    import uuid
    
    # Generate unique ticket ID
    ticket_id = str(uuid.uuid4())[:8]
    
    # Load existing tickets
    tickets = load_tickets()
    
    # Create new ticket
    tickets[ticket_id] = {
        "user_id": user_id,
        "user_name": user_name,
        "guild_id": guild_id,
        "guild_name": guild_name,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "status": "open"
    }
    
    # Save tickets
    save_tickets(tickets)
    
    return ticket_id

def get_ticket(ticket_id):
    """Get a specific ticket by ID."""
    tickets = load_tickets()
    return tickets.get(ticket_id)

def update_ticket(ticket_id, updates):
    """Update a ticket with new information."""
    tickets = load_tickets()
    if ticket_id in tickets:
        tickets[ticket_id].update(updates)
        save_tickets(tickets)
        return True
    return False

def close_ticket(ticket_id, closed_by="admin", admin_response=None, admin_responder=None):
    """Close a ticket and mark it as resolved."""
    updates = {
        "status": f"closed_by_{closed_by}",
        "closed_timestamp": datetime.now().isoformat()
    }
    
    if admin_response:
        updates["admin_response"] = admin_response
    if admin_responder:
        updates["admin_responder"] = admin_responder
        updates["response_timestamp"] = datetime.now().isoformat()
    
    return update_ticket(ticket_id, updates)

def delete_ticket(ticket_id):
    """Permanently delete a ticket."""
    tickets = load_tickets()
    if ticket_id in tickets:
        del tickets[ticket_id]
        save_tickets(tickets)
        return True
    return False

def get_user_tickets(user_id, status_filter=None):
    """Get all tickets for a specific user, optionally filtered by status."""
    tickets = load_tickets()
    user_tickets = {}
    
    for ticket_id, ticket in tickets.items():
        if ticket["user_id"] == user_id:
            if status_filter is None or ticket["status"] == status_filter:
                user_tickets[ticket_id] = ticket
    
    return user_tickets

def get_open_tickets():
    """Get all open tickets."""
    tickets = load_tickets()
    open_tickets = {}
    
    for ticket_id, ticket in tickets.items():
        if ticket["status"] == "open":
            open_tickets[ticket_id] = ticket
    
    return open_tickets

def cleanup_old_tickets(days_old=30):
    """Delete tickets older than specified days that are closed."""
    from datetime import datetime, timedelta
    
    tickets = load_tickets()
    cutoff_date = datetime.now() - timedelta(days=days_old)
    tickets_to_delete = []
    
    for ticket_id, ticket in tickets.items():
        # Only delete closed tickets
        if ticket["status"].startswith("closed"):
            ticket_date = datetime.fromisoformat(ticket["timestamp"])
            if ticket_date < cutoff_date:
                tickets_to_delete.append(ticket_id)
    
    # Delete old tickets
    for ticket_id in tickets_to_delete:
        del tickets[ticket_id]
    
    if tickets_to_delete:
        save_tickets(tickets)
    
    return len(tickets_to_delete)