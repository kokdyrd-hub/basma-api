from fastapi import APIRouter, HTTPException
import database
from datetime import datetime

router = APIRouter()


def day_name(date_string):
    try:
        d = datetime.strptime(date_string, "%m/%d/%Y")

        days = {
            "Saturday": "السبت",
            "Sunday": "الأحد",
            "Monday": "الاثنين",
            "Tuesday": "الثلاثاء",
            "Wednesday": "الأربعاء",
            "Thursday": "الخميس",
            "Friday": "الجمعة"
        }

        return days[d.strftime("%A")]
    except:
        return ""


@router.get("/attendance/{emp_no}")
def get_attendance(emp_no: str):

    conn = database.get_db_connection()

    if conn is None:
        raise HTTPException(
            status_code=500,
            detail="Database Connection Failed"
        )

    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                e.emp_no,
                e.emp_name,
                t.sign_date,
                t.sign_timestring
            FROM basma.timerecords1 t
            JOIN payroll.emp e
              ON e.emp_no = TO_NUMBER(t.emp_id)
            WHERE e.emp_no = :1
            ORDER BY TO_DATE(t.sign_date,'MM/DD/YYYY') DESC
        """, [emp_no])

        rows = cur.fetchall()

        result = {}

        for row in rows:

            emp = row[0]
            name = row[1]
            date = row[2]
            times = (row[3] or "").strip()

            if date not in result:

                result[date] = {
                    "emp_no": emp,
                    "emp_name": name,
                    "date": date,
                    "day": day_name(date),
                    "start_time": None,
                    "end_time": None
                }

            parts = times.split()

            if len(parts) == 0:
                continue

            start = parts[0]

            if len(parts) >= 2:
                end = parts[-1]
            else:
                end = None

            if result[date]["start_time"] is None:
                result[date]["start_time"] = start
            else:
                if start < result[date]["start_time"]:
                    result[date]["start_time"] = start

            if end:

                if result[date]["end_time"] is None:
                    result[date]["end_time"] = end
                else:
                    if end > result[date]["end_time"]:
                        result[date]["end_time"] = end

        attendance = list(result.values())

        attendance.sort(
            key=lambda x: datetime.strptime(x["date"], "%m/%d/%Y"),
            reverse=True
        )

        return {
            "success": True,
            "count": len(attendance),
            "attendance": attendance
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        cur.close()
        conn.close()