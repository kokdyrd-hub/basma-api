from fastapi import APIRouter
from pydantic import BaseModel

from database import payroll_connection

router = APIRouter()


class LoginRequest(BaseModel):
    emp_no: int
    password: str


@router.post("/login")
def login(data: LoginRequest):

    conn = payroll_connection()
    cur = conn.cursor()

    sql = """
        SELECT
            e.emp_no,
            e.emp_name
        FROM payroll.emp e
        JOIN payroll.emp_login l
             ON e.emp_no = l.emp_no
        WHERE e.emp_no = :emp_no
          AND l.password = :password
          AND NVL(l.is_active,1)=1
    """

    cur.execute(
        sql,
        emp_no=data.emp_no,
        password=data.password
    )

    row = cur.fetchone()

    if row is None:
        cur.close()
        conn.close()

        return {
            "success": False,
            "message": "رقم الموظف أو كلمة المرور غير صحيحة"
        }

    cur.execute("""
        UPDATE payroll.emp_login
           SET last_login = SYSDATE
         WHERE emp_no = :emp_no
    """, emp_no=data.emp_no)

    conn.commit()

    cur.close()
    conn.close()

    return {
        "success": True,
        "emp_no": row[0],
        "emp_name": row[1]
    }