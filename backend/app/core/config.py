import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


APP_ENV = os.getenv("APP_ENV", "dev")

ENV_FILE = f".env.{APP_ENV}"

load_dotenv(ENV_FILE)


class Settings(BaseSettings):

    APP_NAME: str
    APP_ENV: str
    LOG_LEVEL: str
    AWS_REGION: str
    # ---------- Genesys OAuth ----------
    GENESYS_REGION: str 
    GENESYS_CLIENT_ID: str
    GENESYS_CLIENT_SECRET: str
    GENESYS_REDIRECT_URI: str
    GENESYS_SCOPES: str 
    GENESYS_LOGIN_ENDPOINT:str
    GENESYS_API_HOST:str

    # ---------- Frontend / CORS ----------
    FRONTEND_URL: str 


    @property
    def IS_PROD(self) -> bool:
        return self.APP_ENV.lower() == "prod"

    @property
    def AUTH_URL(self) -> str:
        return f"https://login.{self.GENESYS_REGION}/oauth/authorize"

    @property
    def TOKEN_URL(self) -> str:
        return f"https://login.{self.GENESYS_REGION}/oauth/token"

    @property
    def GENESYS_API_BASE(self) -> str:
        return f"https://api.{self.GENESYS_REGION}"

settings = Settings()