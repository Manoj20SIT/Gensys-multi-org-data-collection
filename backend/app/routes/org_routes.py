import os
import re
from typing import Any, Dict, List, Optional, Set

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.services.credential_provider import CredentialProvider
# from app.services.token_service import TokenService
# from app.services.genesys_client import GenesysClient, create_genesys_client,  get_client_credentials_token
# from app.services.org_processor import OrgProcessor
from app.core.logger import logger
from app.core.exceptions import ClientBuildError, ConfigException
# from app.services.genesys_service import fetch_org_data
from app.services.collection_service import CollectionService
from app.services.billing_http_service import fetch_billing_subscription_overview_http
from app.services.genesys_client import TokenServiceSimple
from app.schemas.response_schemas import RunCollectionResponseSchema
from app.services.excel_export_service import ExcelExportError, ExcelExportService
from app.services.connection_test_service import ConnectionTestService
from app.services.test_connection_permission import build_permission_summary
import httpx
from fastapi import APIRouter, Query
router = APIRouter(prefix="/api", tags=["org"])
    
    
class RunCollectionRequest(BaseModel):
    interval: str
    fields: Optional[List[str]] = None


@router.post("/run",response_model=RunCollectionResponseSchema)
def run_collection(req: RunCollectionRequest):
    raw_response= CollectionService().run(
        interval=req.interval,
        fields=req.fields
    )
    # Generate Excel and attach metadata
    # exporter = ExcelExportService(export_dir="exports")
    print(f"result receieved in route is ================ {raw_response} ")
    try:
        file_name = ExcelExportService().generate_excel(raw_response)
    except ExcelExportError as e:
        raise HTTPException(status_code=500, detail=str(e))

    raw_response["file_name"] = file_name
    raw_response["download_url"] = f"/api/run/download/{file_name}"
    # print(f"respose we got is {raw_response}")
    return RunCollectionResponseSchema(**raw_response)

@router.get("/run/download/{file_name}")
def download_collection_file(file_name: str):
    file_path = os.path.join("exports", file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
class BillingHttpRequest(BaseModel):
    interval: str


@router.post("/billing/subscription-overview/http")
def billing_subscription_overview_http(req: BillingHttpRequest):
    provider = CredentialProvider()
    orgs = provider.get_org_credentials()

    # org = next((o for o in orgs if o.org_name == req.org_name), None)
    if not orgs:
        raise HTTPException(status_code=404, detail=f"Org '{req.org_name}' not found in config")

    token_service = TokenServiceSimple()
    results = []
    for org in orgs:
        status, data = fetch_billing_subscription_overview_http(
            org=org,
            token_service=token_service,
            interval=req.interval
        )
        results.append({
            "org_name": org.org_name,
            "status": status,
            "success": status < 400,
            "data": data
        })

    if status >= 400:
        raise HTTPException(status_code=status, detail=data)

    return {
        "interval": req.interval,
        "total_orgs": len(orgs),
        "results": results
    }


class TestConnectionRequest(BaseModel):
    org_name: str
    region: str
    api_base_url: str
    client_id: str
    client_secret: str


# Optional helper class if your tester expects attribute-style object
class OrgInput(BaseModel):
    org_name: str
    region: str
    api_base_url: str
    client_id: str
    client_secret: str


@router.post("/test-connection")
def test_connection(req: TestConnectionRequest):
    tester = ConnectionTestService()

    results: List[dict] = []


    # Build org from frontend payload (instead of provider.get_org_credentials())
    org = OrgInput(
        org_name=req.org_name,
        region=req.region,
        api_base_url=req.api_base_url,
        client_id=req.client_id,
        client_secret=req.client_secret
    )

    try:
        result = tester.test_connection_for_org(org=org)

    except ClientBuildError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "org_name": req.org_name,
                "errorCode": "CLIENT_BUILD_FAILED",
                "message": "Connection setup failed. Please verify api_base_url, region, client_id, and client_secret.",
                "errorMessage": str(e),
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "org_name": req.org_name,
                "errorCode": "UNEXPECTED_ERROR",
                "message": "Connection test failed.",
                "errorMessage": str(e),
            },
        )


    summary = build_permission_summary(
        checks=result.get("checks", []),
        missing_areas=result.get("missingAreas", [])
    )

    results.append({
        "org_name": org.org_name,
        "success": summary["success"],
        "message": "All required permissions are available." if summary["success"] else "Some permissions are missing.",
        "overall": "ok" if summary["success"] else "partial",
        "missingAreas": summary["missingAreas"],
        "permissions_required": summary["permissions_required"]
    })

    

    global_ok = all(r.get("success") for r in results)

    return {
        "total_orgs": 1,
        "success": global_ok,
        "message": "OK" if global_ok else "Permission issues found",
        "results": results
    }
    
def extract_permissions_from_raw_error(raw_error: Any) -> List[str]:
    if isinstance(raw_error, dict):
        msg = raw_error.get("message", "") or ""
    else:
        msg = str(raw_error or "")
    matches = re.findall(r"$$([^$$]+)\]", msg)
    perms: List[str] = []
    for m in matches:
        perms.extend([p.strip() for p in m.split(",") if p.strip()])
    return perms



    
    
    