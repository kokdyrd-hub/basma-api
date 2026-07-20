import oracledb
import os
import glob
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    user = os.getenv("BASMA_USER", "BASMA")
    password = os.getenv("BASMA_PASSWORD", "BASMA")
    host = os.getenv("DB_HOST", "10.0.0.100")
    port = os.getenv("DB_PORT", "1521")
    service = os.getenv("DB_SERVICE", "ORCL")

    # محاولة تفعيل الـ Oracle Client (Thick Mode)
    try:
        # البحث عن مجلد Instant Client في المسارات المشهورة على جهازك
        potential_paths = [
            "C:\\instantclient*",
            "C:\\oracle\\instantclient*",
            "C:\\app\\*\\product\\*\\client_*"
        ]
        client_path = None
        for p in potential_paths:
            found = glob.glob(p)
            if found:
                client_path = found[0]
                break

        if client_path:
            print(f"Found Oracle Client at: {client_path}")
            oracledb.init_oracle_client(lib_dir=client_path)
        else:
            # لو لم نجده في المسارات السابقة، نحاول تفعيله من الـ PATH العادي
            oracledb.init_oracle_client()
            print("Oracle Client initialized from System PATH")
    except Exception as e:
        print(f"Note: Oracle Client already initialized or not found: {e}")

    try:
        dsn = f"{host}:{port}/{service}"
        print(f"Connecting to Oracle (THICK MODE): {dsn} as {user}")

        conn = oracledb.connect(
            user=user,
            password=password,
            dsn=dsn
        )
        print(">>> SUCCESS: DATABASE CONNECTED! <<<")
        return conn
    except Exception as e:
        print(f"!!! Connection Error: {str(e)}")
        return None
