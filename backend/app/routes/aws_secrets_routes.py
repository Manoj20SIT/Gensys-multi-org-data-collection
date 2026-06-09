from fastapi import APIRouter, HTTPException
from botocore.exceptions import ClientError

from app.schemas.aws_secret import (
    SecretCreateRequest,
    SecretUpdateRequest,
    SecretGetRequest,
    SecretDeleteRequest,
    SecretListRequest,
)
# from app.services.aws_secrets_service import (
#     create_secret,
#     get_secret_value,
#     update_secret,
#     delete_secret,
#     list_secrets,
#     check_permissions,
# )

router = APIRouter(prefix="/aws/secrets", tags=["AWS Secrets"])


# @router.get("/health")
# def aws_permissions(region: str | None = None):
#     try:
#         return check_permissions(region=region)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"AWS permission check failed: {str(e)}")


# @router.post("/create")
# def create_secret_route(req: SecretCreateRequest):
#     try:
#         data = create_secret(
#             name=req.name,
#             secret_string=req.secret_string,
#             description=req.description,
#             tags=req.tags,
#             region=req.region,
#         )
#         return {"ok": True, "message": "Secret created", "data": data}
#     except ClientError as e:
#         raise HTTPException(status_code=400, detail=e.response["Error"]["Message"])
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/get")
# def get_secret_route(req: SecretGetRequest):
#     try:
#         data = get_secret_value(secret_id=req.secret_id, region=req.region)
#         return {"ok": True, "message": "Secret fetched", "data": data}
#     except ClientError as e:
#         raise HTTPException(status_code=400, detail=e.response["Error"]["Message"])
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.put("/update")
# def update_secret_route(req: SecretUpdateRequest):
#     try:
#         data = update_secret(secret_id=req.secret_id, secret_string=req.secret_string, region=req.region)
#         return {"ok": True, "message": "Secret updated", "data": data}
#     except ClientError as e:
#         raise HTTPException(status_code=400, detail=e.response["Error"]["Message"])
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.delete("/delete")
# def delete_secret_route(req: SecretDeleteRequest):
#     try:
#         data = delete_secret(
#             secret_id=req.secret_id,
#             force_delete_without_recovery=req.force_delete_without_recovery,
#             recovery_window_in_days=req.recovery_window_in_days,
#             region=req.region,
#         )
#         return {"ok": True, "message": "Secret delete requested", "data": data}
#     except ClientError as e:
#         raise HTTPException(status_code=400, detail=e.response["Error"]["Message"])
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/list")
# def list_secrets_route(req: SecretListRequest):
#     try:
#         data = list_secrets(region=req.region, max_results=req.max_results)
#         return {"ok": True, "message": "Secrets listed", "data": data}
#     except ClientError as e:
#         raise HTTPException(status_code=400, detail=e.response["Error"]["Message"])
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
