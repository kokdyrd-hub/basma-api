from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    db_host: str
    db_port: int
    db_service: str

    payroll_user: str
    payroll_password: str

    basma_user: str
    basma_password: str

    class Config:
        env_file = ".env"


settings = Settings()