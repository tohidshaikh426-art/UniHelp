# supabase_client.py
# Supabase Database Client for UniHelp

from supabase import create_client, Client
import os
from datetime import datetime

# NOTE: Do NOT use load_dotenv() - Vercel sets environment variables directly
# load_dotenv() only works for local development with .env files

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Initialize Supabase client - use service_role key if available (bypasses RLS)
if SUPABASE_URL and SUPABASE_KEY:
    try:
        # Use service_role key if available for admin operations, otherwise use anon key
        api_key = SUPABASE_SERVICE_KEY if SUPABASE_SERVICE_KEY else SUPABASE_KEY
        print(f"🔧 Initializing Supabase client...")
        print(f"URL: {SUPABASE_URL[:30]}...")
        print(f"Key length: {len(api_key)} chars")
        supabase: Client = create_client(SUPABASE_URL, api_key)
        print("✅ Supabase Connected Successfully")
        if SUPABASE_SERVICE_KEY:
            print("🔑 Using Service Role Key (RLS bypassed)")
        else:
            print("🔑 Using Anon Key (RLS enabled)")
    except Exception as e:
        print(f"❌ Supabase Connection Failed: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        supabase = None
else:
    print("⚠️  Supabase credentials not found. Using fallback mode.")
    print(f"All env vars: URL={SUPABASE_URL is not None}, KEY={SUPABASE_KEY is not None}, SERVICE_KEY={SUPABASE_SERVICE_KEY is not None}")
    supabase = None


class DatabaseClient:
    """Database operations wrapper for Supabase"""
    
    def __init__(self):
        self.client = supabase
    
    # User Operations
    def get_user_by_email(self, email):
        """Get user by email"""
        if not self.client:
            return None
        
        response = self.client.table('user').select('*').eq('email', email).execute()
        return response.data[0] if response.data else None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        if not self.client:
            return None
        
        response = self.client.table('user').select('*').eq('userid', user_id).execute()
        return response.data[0] if response.data else None
    
    def get_all_users(self):
        """Get all users"""
        if not self.client:
            return []
        
        response = self.client.table('user').select('*').order('created_at', desc=True).execute()
        return response.data
    
    def create_user(self, user_data):
        """Create new user"""
        if not self.client:
            return None
        
        response = self.client.table('user').insert(user_data).execute()
        return response.data[0] if response.data else None
    
    def update_user(self, user_id, data):
        """Update user"""
        if not self.client:
            return None
        
        response = self.client.table('user').update(data).eq('userid', user_id).execute()
        return response.data[0] if response.data else None
    
    # Ticket Operations
    def get_all_tickets(self):
        """Get all tickets with user info and technician info"""
        if not self.client:
            return []
        
        # First, get all tickets with creator info
        response = self.client.table('ticket').select('''
            *,
            user!ticket_userid_fkey(name, email, role)
        ''').order('createdat', desc=True).execute()
        
        tickets = response.data if response.data else []
        
        # Get all technicians for lookup
        tech_response = self.client.table('user').select('userid, name, email').eq('role', 'technician').execute()
        technicians_data = tech_response.data if tech_response.data else []
        
        # Create a dictionary with both int and string keys for flexibility
        technicians = {}
        for tech in technicians_data:
            tech_id = str(tech['userid'])
            technicians[tech_id] = tech
            technicians[tech['userid']] = tech  # Also store with int key
        
        # Manually add technician info to each ticket
        for ticket in tickets:
            # Add creator info
            if ticket.get('user'):
                ticket['user_name'] = ticket['user']['name']
                ticket['user_email'] = ticket['user']['email']
                ticket['user_role'] = ticket['user']['role']
            
            # Add technician info if assigned
            assigned_to = ticket.get('assignedto')
            if assigned_to is not None:
                # Try both string and int lookups
                tech = technicians.get(assigned_to) or technicians.get(str(assigned_to))
                if tech:
                    ticket['technician_name'] = tech['name']
                    ticket['technician_email'] = tech['email']
        
        return tickets
    
    def get_ticket_by_id(self, ticket_id):
        """Get ticket by ID with user info and technician info"""
        if not self.client:
            return None
        
        # Get ticket with creator info
        response = self.client.table('ticket').select('''
            *,
            user!ticket_userid_fkey(name, email, role)
        ''').eq('ticketid', ticket_id).execute()
        
        ticket = response.data[0] if response.data else None
        
        if not ticket:
            return None
        
        # Flatten user data for backward compatibility
        if ticket.get('user'):
            ticket['user_name'] = ticket['user']['name']
            ticket['user_email'] = ticket['user']['email']
            ticket['user_role'] = ticket['user']['role']
        
        # Get technician info if assigned
        assigned_to = ticket.get('assignedto')
        if assigned_to is not None:
            # Fetch technician data
            tech_response = self.client.table('user').select('userid, name, email')\
                .eq('userid', assigned_to)\
                .eq('role', 'technician')\
                .execute()
            
            if tech_response.data and len(tech_response.data) > 0:
                tech = tech_response.data[0]
                ticket['technician_name'] = tech['name']
                ticket['technician_email'] = tech['email']
        
        return ticket
    
    def create_ticket(self, ticket_data):
        """Create new ticket"""
        if not self.client:
            return None
        
        response = self.client.table('ticket').insert(ticket_data).execute()
        return response.data[0] if response.data else None
    
    def update_ticket(self, ticket_id, data):
        """Update ticket"""
        if not self.client:
            return None
        
        response = self.client.table('ticket').update(data).eq('ticketid', ticket_id).execute()
        return response.data[0] if response.data else None
    
    def get_tickets_by_user(self, user_id):
        """Get tickets by user ID"""
        if not self.client:
            return []
        
        response = self.client.table('ticket').select('*').eq('userid', user_id).order('createdat', desc=True).execute()
        return response.data
    
    def get_tickets_by_technician(self, technician_id):
        """Get tickets assigned to technician"""
        if not self.client:
            return []
        
        response = self.client.table('ticket').select('*').eq('assignedto', technician_id).order('createdat', desc=True).execute()
        return response.data
    
    # Comment Operations
    def get_comments_by_ticket(self, ticket_id):
        """Get comments for a ticket"""
        if not self.client:
            return []
        
        response = self.client.table('comment').select('''
            *,
            user!comment_userid_fkey(name, email, role)
        ''').eq('ticketid', ticket_id).order('createdat', desc=False).execute()
        return response.data
    
    def create_comment(self, comment_data):
        """Create new comment"""
        if not self.client:
            return None
        
        response = self.client.table('comment').insert(comment_data).execute()
        return response.data[0] if response.data else None
    
    # Statistics Operations
    def get_ticket_statistics(self):
        """Get ticket statistics"""
        if not self.client:
            return {}
        
        # Get count by status
        response = self.client.rpc('count_tickets_by_status').execute()
        return response.data
    
    def get_user_count_by_role(self):
        """Get user count by role"""
        if not self.client:
            return []
        
        response = self.client.table('user').select('role').execute()
        roles = response.data
        
        # Count manually in Python
        role_counts = {}
        for user in roles:
            role = user['role']
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return role_counts
    
    # Chat Session Operations
    def get_chat_session_by_id(self, session_id):
        """Get chat session by ID"""
        if not self.client:
            return None
        
        response = self.client.table('chat_session').select('*').eq('sessionid', session_id).execute()
        return response.data[0] if response.data else None
    
    def create_chat_session(self, session_data):
        """Create new chat session"""
        if not self.client:
            return None
        
        response = self.client.table('chat_session').insert(session_data).execute()
        return response.data[0] if response.data else None
    
    def get_chat_messages_by_session(self, session_id):
        """Get chat messages by session ID"""
        if not self.client:
            return []
        
        response = self.client.table('chat_message').select('*').eq('sessionid', session_id).order('created_at', desc=False).execute()
        return response.data
    
    def create_chat_message(self, message_data):
        """Create new chat message"""
        if not self.client:
            return None
        
        response = self.client.table('chat_message').insert(message_data).execute()
        return response.data[0] if response.data else None
    
    # Live Chat Operations
    def get_live_chat_by_id(self, chat_id):
        """Get live chat by ID"""
        if not self.client:
            return None
        
        response = self.client.table('live_chat').select('*').eq('livechatid', chat_id).execute()
        return response.data[0] if response.data else None
    
    def create_live_chat(self, chat_data):
        """Create new live chat"""
        if not self.client:
            return None
        
        response = self.client.table('live_chat').insert(chat_data).execute()
        return response.data[0] if response.data else None
    
    def update_live_chat(self, chat_id, data):
        """Update live chat"""
        if not self.client:
            return None
        
        response = self.client.table('live_chat').update(data).eq('livechatid', chat_id).execute()
        return response.data[0] if response.data else None
    
    # Additional Helper Methods for Complex Queries
    def get_available_technician(self, time_window):
        """Get available technician (online and recently active)"""
        if not self.client:
            return None
        
        # Get all technicians first
        response = self.client.table('user').select('''
            userid, name, email,
            user_presence(status, last_seen)
        ''').eq('role', 'technician').eq('isapproved', True).execute()
        
        technicians = response.data
        
        # Filter in Python for complex logic
        now = datetime.now()
        for tech in technicians:
            presence = tech.get('user_presence')
            if presence and presence.get('status') == 'online':
                last_seen_str = presence.get('last_seen')
                if last_seen_str:
                    try:
                        last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                        time_diff = now - last_seen
                        if time_diff.total_seconds() <= time_window * 60:  # Convert minutes to seconds
                            # Check if not in active live chat
                            active_chats = self.client.table('live_chat').select('*').eq('technicianid', tech['userid']).eq('status', 'active').execute()
                            if not active_chats.data:
                                return tech
                    except:
                        continue
        
        return None
    
    # Password Reset Operations
    def create_password_reset_token(self, token_data):
        """Create password reset token"""
        if not self.client:
            return None
        
        response = self.client.table('password_reset_tokens').insert(token_data).execute()
        return response.data[0] if response.data else None
    
    def get_reset_token_by_token(self, token):
        """Get reset token by token string"""
        if not self.client:
            return None
        
        response = self.client.table('password_reset_tokens').select('*').eq('token', token).eq('used', False).execute()
        return response.data[0] if response.data else None
    
    def mark_token_as_used(self, token):
        """Mark reset token as used"""
        if not self.client:
            return None
        
        response = self.client.table('password_reset_tokens').update({'used': True}).eq('token', token).execute()
        return response.data[0] if response.data else None
    
    def delete_expired_tokens(self, email):
        """Delete expired tokens for an email"""
        if not self.client:
            return
        
        from datetime import datetime
        now = datetime.now().isoformat()
        self.client.table('password_reset_tokens').delete().eq('email', email).lt('expires_at', now).execute()


# Create global database instance
db = DatabaseClient()
