from fastapi import FastAPI

from auth import router as auth_router
from attendance import router as attendance_router

app = FastAPI(title="Basma Attendance API")

app.include_router(auth_router)
app.include_router(attendance_router)