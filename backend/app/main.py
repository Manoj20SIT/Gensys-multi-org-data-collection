import os

from app.core.config import APP_ENV, ENV_FILE, settings
from app.core.logger import logger
from app.core.aws_secrets import aws_startup_check
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.db import init_db

from app.routes.auth_routes import router as auth_router
from app.routes.org_routes import router as org_router
from app.routes.protected_routes import router as protected_router
from app.core.exception_handlers import app_exception_handler, unhandled_exception_handler
from app.core.exceptions import AppException
from app.routes.org_config_routes import router as org_config_router
from app.routes.health_routes import router as health_router
from app.routes.aws_secrets_routes import router as aws_secrets_router
import inspect
from PureCloudPlatformClientV2.apis.billing_api import BillingApi

app = FastAPI(title="Genesys OAuth ")
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    logger.info("Starting Genesys Collector Application")
    # init_db()  
    logger.info(f"Environment     : {APP_ENV}")  
    logger.info(f"Environment File: {ENV_FILE}")
    logger.info(f"Application Name: {settings.APP_NAME}")
    logger.info(f"Log Level       : {settings.LOG_LEVEL}")
    print(f"the frontend url is {settings.FRONTEND_URL}")
    # aws_startup_check()  # <-- AWS verify + list secrets
    # logger.info(f"Genesys Region  : {settings.GENESYS_REGION}")
    logger.info(f"CWD: {os.getcwd()}")
    logger.success("Application started successfully")
app.include_router(auth_router)
app.include_router(protected_router)
app.include_router(org_router)
app.include_router(org_config_router)
app.include_router(health_router)
app.include_router(aws_secrets_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
if __name__ == "__main__":
    startup()