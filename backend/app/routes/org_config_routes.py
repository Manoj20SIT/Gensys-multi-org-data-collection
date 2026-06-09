from fastapi import APIRouter, HTTPException, Body
from app.services.org_config_service import OrgConfigService
from app.core.exceptions import ConfigException

router = APIRouter(prefix="/api/orgs", tags=["org-config"])
service = OrgConfigService()


@router.get("")
def list_orgs():
    try:
        orgs = service.list_orgs()

        all_orgs = [{"org_name": o.get("org_name")} for o in orgs if o.get("org_name")]

        return {"total_orgs": len(all_orgs), "orgs": all_orgs}
    except ConfigException as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.post("")
def add_org(payload: dict = Body(...)):
    try:
        created = service.add_org(payload)
        return {"message": "Org added successfully", "org": created}
    except ConfigException as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.put("/{org_name}")
def update_org(org_name: str, payload: dict = Body(...)):
    try:
        updated = service.update_org(org_name, payload)
        return {"message": "Org updated successfully", "org": updated}
    except ConfigException as e:
        status = 404 if "not found" in e.message.lower() else 400
        raise HTTPException(status_code=status, detail=e.message)


@router.delete("/{org_name}")
def delete_org(org_name: str):
    try:
        result = service.delete_org(org_name)
        return {"message": "Org deleted successfully", **result}
    except ConfigException as e:
        status = 404 if "not found" in e.message.lower() else 400
        raise HTTPException(status_code=status, detail=e.message)
    
    

@router.get("/{org_name}")
def get_org_by_name(org_name: str):
    try:
        orgs = service.list_orgs()
        org = next((o for o in orgs if o.get("org_name", "").lower() == org_name.lower()), None)

        if not org:
            raise HTTPException(status_code=404, detail=f"Org '{org_name}' not found")

        # mask secret in detailed response
        # copy org and mask secret
        safe_org = dict(org)
        safe_org["client_secret"] = "********" 
        
        print(f"the og details are = {safe_org}")

        return safe_org
    except ConfigException as e:
        raise HTTPException(status_code=400, detail=e.message)