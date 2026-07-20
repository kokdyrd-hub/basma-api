import database
from supabase import create_client, Client
import time
from datetime import datetime

# إعدادات Supabase
SUPABASE_URL = "https://gwfapapzoqhhyoochmlw.supabase.co"
SUPABASE_KEY = "sb_publishable_L8n5nNfjgkNjSB8qPp6jeg_J9qpmTHe"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def sync_attendance():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting Deep Sync (Last 90 days)...")
    conn = database.get_db_connection()
    if not conn: return
    cur = conn.cursor()
    try:
        # جلب البيانات لآخر 90 يوماً لضمان تغطية شهر يونيو ويوليو بالكامل
        cur.execute("""
            SELECT card_id, emp_id, sign_date, sign_timestring
            FROM basma.timerecords1
            WHERE TO_DATE(sign_date, 'MM/DD/YYYY') >= TRUNC(SYSDATE) - 90
            ORDER BY TO_DATE(sign_date, 'MM/DD/YYYY') DESC
        """)
        rows = cur.fetchall()

        if not rows:
            print("--- No records found in Oracle.")
            return

        print(f"--- Found {len(rows)} records in Oracle.")

        sync_data = []
        for row in rows:
            emp_id = str(row[1]).strip().zfill(8)
            sync_data.append({
                "card_id": str(row[0]) if row[0] else "",
                "emp_id": emp_id,
                "sign_date": str(row[2]).strip(),
                "sign_timestring": str(row[3]).strip() if row[3] else ""
            })

        # الرفع للسحاب
        if sync_data:
            for i in range(0, len(sync_data), 100):
                batch = sync_data[i:i+100]
                supabase.table("timerecords1").upsert(batch).execute()
            print(">>> SUCCESS: All records (June & July) synced to Supabase.")

    except Exception as e: print(f"!!! Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("Delta Auto-Sync v3.5 (Deep History) Active")
    while True:
        sync_attendance()
        print("Waiting 60 seconds...")
        time.sleep(60)
