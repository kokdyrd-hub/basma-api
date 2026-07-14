import oracledb
from config import settings


# لا تستخدم Thick Mode على Render
# سيتم استخدام Thin Mode تلقائياً


def payroll_connection():
    return oracledb.connect(
        user=settings.payroll_user,
        password=settings.payroll_password,
        dsn=f"{settings.db_host}:{settings.db_port}/{settings.db_service}"
    )


def basma_connection():
    return oracledb.connect(
        user=settings.basma_user,
        password=settings.basma_password,
        dsn=f"{settings.db_host}:{settings.db_port}/{settings.db_service}"
    )