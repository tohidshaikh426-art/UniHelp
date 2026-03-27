#!/usr/bin/env python3
"""
Check Supabase Table Schema
Displays actual column names for comment and other tables
"""

from supabase_client import db

def check_table_schema():
    """Check actual column names in Supabase tables"""
    
    if not db.client:
        print("❌ Supabase client not available")
        return
    
    tables_to_check = [
        'comment',
        'ticket', 
        'user',
        'chat_message',
        'chat_session'
    ]
    
    print("=" * 60)
    print("📊 Supabase Table Schema Check")
    print("=" * 60)
    
    for table_name in tables_to_check:
        print(f"\n📋 Table: {table_name}")
        print("-" * 60)
        
        try:
            # Get one record to see actual column names
            response = db.client.table(table_name).select('*').limit(1).execute()
            
            if response.data and len(response.data) > 0:
                columns = list(response.data[0].keys())
                print(f"   Columns ({len(columns)}):")
                for col in sorted(columns):
                    # Highlight timestamp columns
                    if 'at' in col.lower() or 'time' in col.lower() or 'date' in col.lower():
                        print(f"      ⏰ {col}")
                    else:
                        print(f"      {col}")
            else:
                print("   ⚠️  Table is empty - cannot determine columns")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Schema check complete!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        check_table_schema()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
