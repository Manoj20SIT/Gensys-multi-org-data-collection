import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.services.credential_provider import CredentialProvider
# from app.services.token_service import TokenService
# from app.services.genesys_client import GenesysClient, create_genesys_client,  get_client_credentials_token
# from app.services.org_processor import OrgProcessor
from app.core.logger import logger
from app.core.exceptions import ConfigException
# from app.services.genesys_service import fetch_org_data
from app.services.collection_service import CollectionService
from app.services.billing_http_service import fetch_billing_subscription_overview_http
from app.services.genesys_client import TokenServiceSimple
from app.schemas.response_schemas import RunCollectionResponseSchema
from app.services.excel_export_service import ExcelExportError, ExcelExportService
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



    
    
    