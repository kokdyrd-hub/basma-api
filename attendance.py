from fastapi import APIRouter
from database import basma_connection

router = APIRouter()

@router.get("/attendance/{emp_no}")
def attendance(emp_no: int):

    conn = basma_connection()
    cur = conn.cursor()

    sql = """
    SELECT
        SIGN_DATE,
        SIGN_TIMESTRING
    FROM basma.TIMERECORDS1
    WHERE EMP_ID = :emp_no
    ORDER BY TO_DATE(SIGN_DATE,'MM/DD/YYYY') DESC
    """

    cur.execute(sql, emp_no=str(emp_no).zfill(8))

    rows = cur.fetchall()

    result = []

    for r in rows:
        result.append({
            "date": r[0],
            "time": r[1]
        })

    cur.close()
    conn.close()

    return result