from typing import List, Optional, Set
from PureCloudPlatformClientV2.rest import ApiException

from app.services.credential_provider import CredentialProvider
from app.services.genesys_client import get_client_credentials_token, create_genesys_client
from app.services.universal_api_engine import UniversalApiEngine
from app.services.task_factory import genesys_apitasks
from app.services.response_mapper import map_to_ui_fields
from app.services.field_to_tasks import FIELD_TO_TASKS
from app.services.billing_http_service import fetch_billing_subscription_overview_http
from app.services.billing_mapper import map_billing_data
from app.services.billing_extractors import extract_ai_experience_tokens, extract_is_in_ramp_period, extract_license_model


class CollectionService:
    def __init__(self):
        self.provider = CredentialProvider()
        self.engine = UniversalApiEngine()

    def _resolve_required_task_keys(self, fields: Optional[List[str]]) -> Optional[Set[str]]:
        if not fields:
            return None
        required: Set[str] = set()
        for f in fields:
            for task_key in FIELD_TO_TASKS.get(f, []):
                required.add(task_key)
        return required

    def _build_client(self, org):
        token, expires_in = get_client_credentials_token(
            api_base_url=org.api_base_url,
            client_id=org.client_id,
            client_secret=org.client_secret
        )
        api_client = create_genesys_client(
            access_token=token,
            api_host=org.api_base_url
        )
        return token, expires_in, api_client

    def _is_auth_error(self, ex: Exception) -> bool:
        # SDK errors
        if isinstance(ex, ApiException):
            return getattr(ex, "status", None) in (401, 403)

        # fallback text check for wrapped errors
        msg = str(ex).lower()
        return ("401" in msg or  "unauthorized" in msg or "forbidden" in msg)

    def _run_for_org_once(self, org, interval: str, fields, required_task_keys, token, expires_in, api_client):
        tasks = genesys_apitasks(interval, required_task_keys=required_task_keys)
        task_result = self.engine.run_tasks(api_client, tasks, org_name=org.org_name)

        raw_data = task_result.get("data", {})
        task_errors = task_result.get("task_errors", [])

        billing_status, billing_data = fetch_billing_subscription_overview_http(
            org=org,
            interval=interval,
            access_token=token
        )
        mapped_billing = map_billing_data(billing_data) if billing_status < 400 else {}
        print(f"-------------------------------------------------------------------")
        print()
        

        billing_metrics = {}
        if billing_status < 400:
            billing_metrics = {
                "isInRampPeriod": extract_is_in_ramp_period(mapped_billing),
                "licenseModel": extract_license_model(mapped_billing),
                "aiExperienceTokens": extract_ai_experience_tokens(mapped_billing),  # optional but recommended
            }
        print("*888888888888888888888888888***********************")
        # IMPORTANT: pass billing_metrics here
        metrics = map_to_ui_fields(raw_data, fields=fields, billing_metrics=billing_metrics)
        print(f"the new response is {metrics} ")

        org_result = {
            "org_name": org.org_name,
            "success": len(task_errors) == 0 and billing_status < 400,
            "expires_in": expires_in,
            "metrics": metrics,
            "billing_subscription_overview": {
                "status": billing_status,
                "success": billing_status < 400,
                # "mapped": mapped_billing,
                # "metrics": billing_metrics
            }
        }

        return org_result


    def run(self, interval: str, fields: Optional[List[str]] = None):
        orgs = self.provider.get_org_credentials()
        if not orgs:
            return {"total_orgs": 0, "results": [], "message": "No org credentials found"}

        required_task_keys = self._resolve_required_task_keys(fields)
        results = []

        for org in orgs:
            try:
                # first attempt
                token, expires_in, api_client = self._build_client(org)
                try:
                    org_result = self._run_for_org_once(
                        org, interval, fields, required_task_keys, token, expires_in, api_client
                    )
                    
                    results.append(org_result)

                except Exception as e:
                    # retry once only for auth errors
                    if self._is_auth_error(e):
                        token, expires_in, api_client = self._build_client(org)
                        org_result = self._run_for_org_once(
                            org, interval, fields, required_task_keys, token, expires_in, api_client
                        )
                        org_result["token_refreshed"] = True
                        results.append(org_result)
                    else:
                        raise

            except Exception as e:
                results.append({
                    "org_name": org.org_name,
                     "success": False,
                    "error": str(e),
                    "task_errors": []
                })
        
        return {
            "total_orgs": len(orgs),
            "mode": "sequential",
            "requested_fields": fields,
            "results": results
        }

