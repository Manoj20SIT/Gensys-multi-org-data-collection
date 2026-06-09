from fastapi import APIRouter, HTTPException
from app.scripts.check_aws_secrets_permissions import check_aws_secrets_permissions

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/aws-permissions")
def aws_permissions():
    try:
        return check_aws_secrets_permissions()  # no explicit region
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AWS permission check failed: {str(e)}")
