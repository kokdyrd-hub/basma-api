from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import auth
import attendance
import database
import os

app = FastAPI(title="Basma Bridge System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# إعدادات Supabase للرفع (تأكد أنها نفس بياناتك)
SUPABASE_URL = "https://gwfapapzoqhhyoochmlw.supabase.co"
SUPABASE_KEY = "sb_publishable_L8n5nNfjgkNjSB8qPp6jeg_J9qpmTHe"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.post("/sync")
def sync_oracle_to_supabase():
    conn = database.get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Oracle Connection Failed")

    cur = conn.cursor()
    try:
        # 1. جلب البيانات من أوراكل (آخر 30 يوم مثلاً لسرعة المزامنة)
        cur.execute("""
            SELECT card_id, emp_id, sign_date, sign_timestring
            FROM basma.timerecords1
            WHERE TO_DATE(sign_date, 'MM/DD/YYYY') >= SYSDATE - 30
        """)
        rows = cur.fetchall()

        # 2. تجهيز البيانات للتنسيق الذي يفهمه Supabase
        sync_data = []
        for row in rows:
            sync_data.append({
                "card_id": str(row[0]),
                "emp_id": str(row[1]),
                "sign_date": str(row[2]),
                "sign_timestring": str(row[3])
            })

        # 3. الرفع لـ Supabase (استخدام upsert لتجنب التكرار)
        if sync_data:
            # نقوم بالرفع على دفعات (Batches) لضمان الاستقرار
            batch_size = 100
            for i in range(0, len(sync_data), batch_size):
                batch = sync_data[i:i + batch_size]
                supabase.table("timerecords1").upsert(batch).execute()

        return {"success": True, "message": f"تمت مزامنة {len(sync_data)} سجل بنجاح"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

app.include_router(auth.router)
app.include_router(attendance.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
