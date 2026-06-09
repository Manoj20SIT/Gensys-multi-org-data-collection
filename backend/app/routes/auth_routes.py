from fastapi import APIRouter, Request, HTTPException ,Query
from fastapi.responses import RedirectResponse, JSONResponse
import os
from app.core.config import settings
from  app.core.OAuthHandler import OAuthHandler
from app.services.genesys_client import exchange_code_for_token

from pydantic import BaseModel

router = APIRouter()

class CodeRequest(BaseModel):
    code: str


oauth_handler = OAuthHandler(
    client_id=settings.GENESYS_CLIENT_ID,
    redirect_uri=settings.GENESYS_REDIRECT_URI,
    scope=settings.GENESYS_SCOPES,   # or GENESYS_SCOPES based on your config
    login_endpoint=settings.GENESYS_LOGIN_ENDPOINT,
)

print("GENESYS ROUTES FILE LOADED")
# 1️⃣ Get Login URL
@router.get("/api/get-login-url")
def get_login_url():
    url = oauth_handler.construct_auth_url()
    return {"authUrl": url}


# 2️⃣ Callback Endpoint
@router.get("/api/callback")
def oauth_callback(code: str):
    try:
        token_data = exchange_code_for_token(code)

        access_token = token_data["access_token"]

        # In production: store in session / DB
        return JSONResponse({
            "message": "Login successful",
            "access_token": access_token
        })

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/exchange-code")
def exchange_code(request: CodeRequest):
    try:
        token_data = exchange_code_for_token(request.code)
        return token_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
