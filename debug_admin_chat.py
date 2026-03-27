#!/usr/bin/env python3
"""
Debug script to test admin-to-technician chat connection
Run this after admin sends a message to technician
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables for local testing
from dotenv import load_dotenv
load_dotenv()

from supabase_client import db
from datetime import datetime

def debug_admin_chat_connection():
    """Debug the complete flow of admin connecting to technician"""
    
    print("="*60)
    print("🔍 DEBUG: Admin to Technician Chat Connection")
    print("="*60)
    
    if not db.client:
        print("❌ Supabase client not available!")
        return
    
    # Get all technicians
    print("\n1️⃣  Getting all technicians...")
    tech_response = db.client.table('user').select('*').eq('role', 'technician').eq('isapproved', True).execute()
    technicians = tech_response.data if tech_response.data else []
    
    if not technicians:
        print("❌ No approved technicians found!")
        return
    
    print(f"✅ Found {len(technicians)} technician(s)")
    for tech in technicians:
        print(f"   • ID: {tech['userid']}, Name: {tech['name']}, Email: {tech['email']}")
    
    # Check each technician's live chats
    for tech in technicians:
        tech_id = tech['userid']
        print(f"\n2️⃣  Checking live chats for technician {tech['name']} (ID: {tech_id})...")
        
        # Query 1: Simple query without JOINs
        print(f"   📊 Query 1: Simple SELECT * FROM live_chat WHERE technicianid={tech_id} AND status='active'")
        simple_response = db.client.table('live_chat').select('*')\
            .eq('technicianid', tech_id)\
            .eq('status', 'active')\
            .execute()
        
        simple_chats = simple_response.data if simple_response.data else []
        print(f"   ✅ Simple query found {len(simple_chats)} active chat(s)")
        
        for i, chat in enumerate(simple_chats):
            print(f"      Chat #{i+1}:")
            print(f"         livechatid: {chat['livechatid']}")
            print(f"         sessionid: {chat['sessionid']}")
            print(f"         status: {chat.get('status')}")
            print(f"         started_at: {chat.get('started_at', 'N/A')}")
        
        # Query 2: With JOINs (this is what get_new_chats uses)
        print(f"\n   📊 Query 2: With JOINs to get user info...")
        try:
            join_response = db.client.table('live_chat').select('''
                *,
                chat_session(userid),
                user!chat_session_userid_fkey(name, email, role)
            ''').eq('technicianid', tech_id).eq('status', 'active').execute()
            
            join_chats = join_response.data if join_response.data else []
            print(f"   ✅ JOIN query found {len(join_chats)} active chat(s)")
            
            for i, chat in enumerate(join_chats):
                print(f"      Chat #{i+1}:")
                print(f"         livechatid: {chat['livechatid']}")
                print(f"         sessionid: {chat['sessionid']}")
                print(f"         user data: {chat.get('user', 'N/A')}")
                
                # Get messages
                msg_response = db.client.table('chat_message').select('*')\
                    .eq('sessionid', chat['sessionid'])\
                    .order('created_at', desc=True)\
                    .limit(3)\
                    .execute()
                
                messages = msg_response.data if msg_response.data else []
                print(f"         Last {len(messages)} message(s):")
                for msg in messages[:3]:
                    sender = msg.get('sender', 'unknown')
                    message = msg.get('message', '')[:50]
                    print(f"            [{sender}]: {message}...")
        
        except Exception as e:
            print(f"   ❌ JOIN query failed: {e}")
            print(f"      This might be due to missing foreign key constraints or RLS policies")
        
        # Query 3: Check chat sessions
        if simple_chats:
            print(f"\n   📊 Query 3: Checking related chat_session records...")
            session_ids = [chat['sessionid'] for chat in simple_chats]
            for session_id in session_ids:
                session_response = db.client.table('chat_session').select('*').eq('sessionid', session_id).execute()
                sessions = session_response.data if session_response.data else []
                
                if sessions:
                    session = sessions[0]
                    print(f"      Session ID: {session_id}")
                    print(f"         userid: {session.get('userid')}")
                    print(f"         status: {session.get('status')}")
                    print(f"         source: {session.get('source', 'N/A')}")
                    print(f"         created_at: {session.get('created_at', 'N/A')}")
                    
                    # Get user who created the session
                    user_id = session.get('userid')
                    if user_id:
                        user_response = db.client.table('user').select('*').eq('userid', user_id).execute()
                        users = user_response.data if user_response.data else []
                        if users:
                            user = users[0]
                            print(f"         Created by: {user.get('name')} ({user.get('role')}) - Email: {user.get('email')}")
                        else:
                            print(f"         ⚠️  User ID {user_id} not found in user table!")
                else:
                    print(f"      ⚠️  No chat_session found for sessionid={session_id}")
    
    print("\n" + "="*60)
    print("✅ Debug complete!")
    print("="*60)
    
    # Summary
    total_simple = sum(len(db.client.table('live_chat').select('*').eq('technicianid', tech['userid']).eq('status', 'active').execute().data or []) for tech in technicians)
    print(f"\n📊 SUMMARY:")
    print(f"   Total technicians: {len(technicians)}")
    print(f"   Total active live chats (simple query): {total_simple}")
    print(f"\n💡 If simple query returns results but JOIN query fails,")
    print(f"   check RLS policies and foreign key constraints.")


if __name__ == '__main__':
    debug_admin_chat_connection()
