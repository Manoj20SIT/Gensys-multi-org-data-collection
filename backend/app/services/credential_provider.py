from typing import List
from app.models.schemas import OrgCredentials
from app.core.config_loader import load_config
from pathlib import Path

from app.services.aws_secrets_service import AwsClientSecretService
class CredentialProvider:
    """
    Current source: config.json
    Future: replace this class with AWS Secrets Manager implementation
    without changing token/client logic.
    """

    def __init__(self, path: str | None = None):
        default_path = Path(__file__).resolve().parents[1] / "config.json"  # app/config.json
        self.path = str(default_path) if path is None else path
        self.secret_service = AwsClientSecretService()

    def get_org_credentials(self) -> List[OrgCredentials]:
        cfg = load_config(self.path)
        orgs = []

        for idx, item in enumerate(cfg.get("org_details", []), start=1):
            conn = item.get("connection", {}) or {}
            org_name = item.get("org_name", "unknown_org")

            # fallback: try connection first, then top-level
            region = conn.get("region") or item.get("region") or ""
            api_base_url = conn.get("api_base_url") or item.get("api_base_url") or ""
            client_id = conn.get("client_id") or item.get("client_id") or ""

            # if secret removed from config, fetch from secrets manager instead
            client_secret = conn.get("client_secret") or item.get("client_secret") or ""
            if not client_secret:
                client_secret = self.secret_service.get_client_secret(org_name) or ""

            # print(f"\nDEBUG ORG #{idx}")
            # print("org_name:", org_name)
            # print("region:", region)
            # print("api_base_url:", api_base_url)
            # print("client_id:", client_id)
            # print("client_secret:", "SET" if client_secret else "MISSING")

            orgs.append(
                OrgCredentials(
                    org_name=org_name,
                    api_base_url=api_base_url.rstrip("/"),
                    region=region,
                    client_id=client_id,
                    client_secret=client_secret,
                )
            )
        return orgs