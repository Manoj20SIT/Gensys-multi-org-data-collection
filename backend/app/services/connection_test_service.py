import re
from typing import Any, Dict, List

from app.services.genesys_client import create_genesys_client, get_client_credentials_token
from app.services.genesys_permission_probes import build_permission_probe_tasks
from app.services.universal_api_engine import UniversalApiEngine
from app.core.exceptions import ClientBuildError


class ConnectionTestService:
    def __init__(self):
        self.engine = UniversalApiEngine()

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

    def _classify(self, status_code: int) -> str:
        if status_code == 200:
            return "ok"
        if status_code == 401:
            return "unauthorized"
        if status_code == 403:
            return "forbidden"
        if status_code == 404:
            return "not_available"
        if status_code >= 500:
            return "server_error"
        return "error"

    def _extract_status_code(self, err_obj: Dict[str, Any]) -> int:
        if not err_obj:
            return 0
        for k in ("status_code", "status", "http"):
            v = err_obj.get(k)
            if isinstance(v, int):
                return v
        ctx = err_obj.get("context") or {}
        for k in ("status_code", "status", "http"):
            v = ctx.get(k)
            if isinstance(v, int):
                return v
        return 0

    def _extract_raw_error(self, err_obj: Dict[str, Any]) -> Any:
        if not err_obj:
            return None
        ctx = err_obj.get("context") or {}
        return (
            err_obj.get("raw_error")
            or ctx.get("raw_error")
            or err_obj.get("raw_body")
            or ctx.get("raw_body")
            or err_obj.get("error")
            or err_obj.get("message")
        )

    def _extract_permissions(self, raw_error: Any) -> List[str]:
        if isinstance(raw_error, dict):
            msg = raw_error.get("message", "") or ""
        else:
            msg = str(raw_error or "")
        matches = re.findall(r"$$([^$$]+)\]", msg)
        perms: List[str] = []
        for m in matches:
            perms.extend([p.strip() for p in m.split(",") if p.strip()])
        return sorted(set(perms))

    def test_connection_for_org(self, org) -> Dict[str, Any]:
            # 1) Handle client creation errors explicitly
        try:
            print(f"trying to build client for the org ={org}")
            token, expires_in, api_client = self._build_client(org)
            print(f"api client is {api_client}")
        except Exception as e:
            raise ClientBuildError(
            f"Connection setup failed for org={getattr(org, 'org_name', 'unknown')}: {e}"
        ) from e

            

        # 2) Handle task execution errors separately (optional but recommended)
        try:
            tasks = build_permission_probe_tasks()
            run_result = self.engine.run_tasks(api_client, tasks, org_name=org.org_name)
        except Exception as e:
            err_msg = str(e) or "Failed while running permission checks"
            print(f"[TASK_EXECUTION_ERROR] org={org.org_name} error={err_msg}")

            return {
                "org_name": org.org_name,
                "success": False,
                "overall": "error",
                "expires_in": expires_in,
                "checks": [],
                "missingAreas": [],
                "userMessage": "Connection established, but permission checks failed to execute.",
                "errorCode": "TASK_EXECUTION_FAILED",
                "errorMessage": err_msg
            }

        data = run_result.get("data", {})
        task_errors = run_result.get("task_errors", [])

        print(f"\n=== org: {org.org_name} === task_errors={task_errors}")
        for e in task_errors:
            key = e.get("task_key") or e.get("key")
            status = self._extract_status_code(e)
            raw_error = self._extract_raw_error(e)
            print(f"[ERROR] key={key} status={status} raw_error={raw_error}")
        print("=== End errors ===\n")

        error_map: Dict[str, Dict[str, Any]] = {}
        for e in task_errors:
            key = e.get("task_key") or e.get("key")
            if not key:
                continue
            status_code = self._extract_status_code(e)
            raw_error = self._extract_raw_error(e)

            error_map[key] = {
                "http": status_code,
                "raw_error": raw_error,
                "error": e.get("error") or e.get("message") or "Unknown error"
            }

        checks: List[Dict[str, Any]] = []
        for t in tasks:
            if t.key in error_map:
                http = error_map[t.key]["http"]
                state = self._classify(http)
                raw_error = error_map[t.key]["raw_error"]
                missing_permissions = self._extract_permissions(raw_error)

                checks.append({
                    "key": t.key,
                    "status": state,
                    "http": http,
                    "method": f"{t.api_name}.{t.method_name}",
                    "raw_error": raw_error,
                    "missing_permissions": missing_permissions,
                    "message": (
                        f"Missing or invalid permission for {t.key}. "
                        f"Ask admin to grant required role/division access."
                        if state in ("forbidden", "unauthorized")
                        else error_map[t.key]["error"]
                    )
                })
            else:
                checks.append({
                    "key": t.key,
                    "status": "ok",
                    "http": 200,
                    "method": f"{t.api_name}.{t.method_name}",
                    "raw_error": None,
                    "missing_permissions": [],
                    "message": "Authorized"
                })

        missing_areas = [c["key"] for c in checks if c["status"] in ("forbidden", "unauthorized")]

        if all(c["status"] == "ok" for c in checks):
            overall = "ok"
        elif missing_areas:
            overall = "partial"
        else:
            overall = "error"

        return {
            "org_name": org.org_name,
            "success": overall == "ok",
            "overall": overall,
            "expires_in": expires_in,
            "checks": checks,
            "missingAreas": missing_areas,
            "userMessage": (
                "All required permissions are available."
                if overall == "ok"
                else "Some permissions are missing. Please grant required roles/divisions and retry Test Connection."
            )
        }