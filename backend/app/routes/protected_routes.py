from fastapi import APIRouter, Request, HTTPException
from app.core.config import settings
# from app.services.genesys_api_service import fetch_customer_orgs

router = APIRouter(prefix="/api", tags=["protected"])

# @router.get("/customer-orgs")
# def customer_orgs(request: Request):
#     session_id = request.cookies.get(settings.COOKIE_NAME)
#     if not session_id:
#         raise HTTPException(status_code=401, detail="Not authenticated")

#     return "hello"