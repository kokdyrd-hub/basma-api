from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import database
from datetime import datetime

router = APIRouter()

class LoginRequest(BaseModel):
    emp_no: int
    password: str

class ChangePasswordRequest(BaseModel):
    emp_no: int
    old_password: str
    new_password: str

class AdminResetPasswordRequest(BaseModel):
    emp_no: int
    new_password: str

@router.post("/login")
def login(req: LoginRequest):
    conn = database.get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database Connection Failed")

    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT e.EMP_NO, e.EMP_NAME, l.PASSWORD
            FROM payroll.emp e
            LEFT JOIN payroll.emp_login l ON e.EMP_NO = l.EMP_NO
            WHERE e.EMP_NO = :1
        """, [req.emp_no])

        row = cur.fetchone()
        if row is None:
            return {"success": False, "message": "رقم الموظف غير موجود"}

        emp_no, emp_name, db_password = row
        actual_password = str(db_password) if db_password is not None else "0000"

        if str(req.password) != actual_password:
            return {"success": False, "message": "كلمة المرور غير صحيحة"}

        if db_password is not None:
            cur.execute("UPDATE payroll.emp_login SET LAST_LOGIN = SYSDATE WHERE EMP_NO = :1", [emp_no])
            conn.commit()

        return {
            "success": True,
            "emp_no": emp_no,
            "emp_name": emp_name,
            "message": "تم تسجيل الدخول"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cur.close()
        conn.close()

@router.post("/change-password")
def change_password(req: ChangePasswordRequest):
    conn = database.get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database Connection Failed")

    cur = conn.cursor()
    try:
        cur.execute("SELECT PASSWORD FROM payroll.emp_login WHERE EMP_NO = :1", [req.emp_no])
        row = cur.fetchone()

        old_db_pass = str(row[0]) if row else "0000"

        if str(req.old_password) != old_db_pass:
            return {"success": False, "message": "كلمة المرور القديمة غير صحيحة"}

        if row:
            cur.execute("""
                UPDATE payroll.emp_login
                SET PASSWORD = :1, LAST_LOGIN = SYSDATE
xx                WHERE EMP_NO = :2
            """, [str(req.new_password), req.emp_no])
        else:
            cur.execute("""
                INSERT INTO payroll.emp_login (EMP_NO, PASSWORD, IS_ACTIVE, CREATED_AT)
                VALUES (:1, :2, 1, SYSDATE)
            """, [req.emp_no, str(req.new_password)])

        conn.commit()
        return {"success": True, "message": "

تم تغيير كلمة المرور بنجاح"}

    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cur.close()
        conn.close()

@router.post("/admin-reset-password")
def admin_reset_password(req: AdminResetPasswordRequest):
    conn = database.get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database Connection Failed")

    cur = conn.cursor()
    try:
        # التأكد أولاً من وجود الموظف في جدول الموظفين
        cur.execute("SELECT EMP_NO FROM payroll.emp WHERE EMP_NO = :1", [req.emp_no])
        if cur.fetchone() is None:
            return {"success": False, "message": "رقم الموظف غير موجود في النظام"}

        cur.execute("SELECT EMP_NO FROM payroll.emp_login WHERE EMP_NO = :1", [req.emp_no])
        row = cur.fetchone()

        if row:
            cur.execute("""
                UPDATE payroll.emp_login
                SET PASSWORD = :1, LAST_LOGIN = SYSDATE
                WHERE EMP_NO = :2
            """, [str(req.new_password), req.emp_no])
        else:
            cur.execute("""
                INSERT INTO payroll.emp_login (EMP_NO, PASSWORD, IS_ACTIVE, CREATED_AT)
                VALUES (:1, :2, 1, SYSDATE)
            """, [req.emp_no, str(req.new_password)])

        conn.commit()
        return {"success": True, "message": "تم إعادة تعيين كلمة المرور بنجاح"}

    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        cur.close()
        conn.close()
