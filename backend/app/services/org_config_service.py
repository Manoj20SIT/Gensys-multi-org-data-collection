from typing import Dict, Any, List
from app.core.config_loader import load_config, save_config
from app.core.exceptions import ConfigException
from app.services.aws_secrets_service import AwsClientSecretService


class OrgConfigService:
    def __init__(self, path: str | None = None):
        self.path = path
        self.secret_service = AwsClientSecretService()

    def list_orgs(self) -> List[Dict[str, Any]]:
        cfg = load_config(self.path)
        return cfg.get("org_details", [])

    
    def add_org(self, org_payload: Dict[str, Any]) -> Dict[str, Any]:
        cfg = load_config(self.path)
        orgs = cfg.setdefault("org_details", [])

        org_name = org_payload.get("org_name")
        client_secret = org_payload.get("client_secret")

        if not org_name:
            raise ConfigException(
                message="org_name is required",
                context={"module": "services.org_config_service", "function": "add_org"},
            )

        if not client_secret:
            raise ConfigException(
                message="client_secret is required",
                context={"module": "services.org_config_service", "function": "add_org"},
            )

        if any(o.get("org_name") == org_name for o in orgs):
            raise ConfigException(
                message=f"Org '{org_name}' already exists",
                context={"module": "services.org_config_service", "function": "add_org"},
            )

        safe_payload = dict(org_payload)
        safe_payload.pop("client_secret", None)

        # 1) save secret in AWS
        self.secret_service.upsert_client_secret(org_name, client_secret)

        # 2) save org config (without secret)
        orgs.append(safe_payload)
        save_config(cfg, self.path)

        return safe_payload

    def update_org(self, org_name: str, update_payload: Dict[str, Any]) -> Dict[str, Any]:
        cfg = load_config(self.path)
        orgs = cfg.setdefault("org_details", [])

        if "client_secret" in update_payload and not update_payload.get("client_secret"):
            raise ConfigException(
                message="client_secret cannot be empty",
                context={"module": "services.org_config_service", "function": "update_org"},
            )

        client_secret = update_payload.get("client_secret")
        safe_update = dict(update_payload)
        safe_update.pop("client_secret", None)

        for idx, org in enumerate(orgs):
            if org.get("org_name") == org_name:
                # update secret only if provided
                if client_secret:
                    self.secret_service.upsert_client_secret(org_name, client_secret)

                updated = {**org, **safe_update}

                if "connection" in safe_update and isinstance(safe_update["connection"], dict):
                    old_conn = org.get("connection", {})
                    updated["connection"] = {**old_conn, **safe_update["connection"]}

                orgs[idx] = updated
                save_config(cfg, self.path)
                return updated

        raise ConfigException(
            message=f"Org '{org_name}' not found",
            context={"module": "services.org_config_service", "function": "update_org"},
        )

    def delete_org(self, org_name: str) -> Dict[str, Any]:
        cfg = load_config(self.path)
        orgs = cfg.setdefault("org_details", [])

        filtered = [o for o in orgs if o.get("org_name") != org_name]
        if len(filtered) == len(orgs):
            raise ConfigException(
                message=f"Org '{org_name}' not found",
                context={"module": "services.org_config_service", "function": "delete_org"},
            )

        cfg["org_details"] = filtered
        save_config(cfg, self.path)

        # best-effort cleanup in secrets manager
        self.secret_service.delete_client_secret(org_name)

        return {"deleted_org": org_name}