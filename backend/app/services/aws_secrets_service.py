import json
import os
from typing import Any, Dict, Optional

from app.core.aws_session import get_boto_session, resolve_region
from botocore.exceptions import ClientError

class AwsClientSecretService:
    def _client(self,region: Optional[str] = None):
        session = get_boto_session()
        final_region = resolve_region(session, region)
        return session.client("secretsmanager", region_name=final_region), final_region
    
    def build_secret_name(self, org_name: str) -> str:
        # env = (os.getenv("APP_ENV") or "dev").lower()
        return f"genesys/org/{org_name}/credentials"




    def create_secret(
        self,
        secret_name: str,
        client_secret: str,
        region: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        client, final_region = self._client(region)

        payload = {
            "Name": secret_name,
            "SecretString": json.dumps({"client_secret": client_secret}),
        }
        if description:
            payload["Description"] = description
        if tags:
            payload["Tags"] = [{"Key": k, "Value": v} for k, v in tags.items()]

        resp = client.create_secret(**payload)
        return {
            "name": resp.get("Name"),
            "arn": resp.get("ARN"),
            "version_id": resp.get("VersionId"),
            "region": final_region,
        }
    

    def get_client_secret(self, org_name: str, region: Optional[str] = None) -> Optional[str]:
        client, _ = self._client(region)
        secret_name = self.build_secret_name(org_name)
        try:
            resp = client.get_secret_value(SecretId=secret_name)
            raw = resp.get("SecretString") or "{}"
            try:
                data = json.loads(raw)
                return data.get("client_secret")
            except Exception:
                # backward compatibility with old plain-text secrets
                return raw
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return None
            raise


    # def get_secret_value(self,secret_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    #     client, final_region = self._client(region)
    #     resp = client.get_secret_value(SecretId=secret_id)
    #     return {
    #         "name": secret_id,
    #         "arn": resp.get("ARN"),
    #         "secret_string": resp.get("SecretString"),
    #         "version_id": resp.get("VersionId"),
    #         "created_date": str(resp.get("CreatedDate")),
    #         "region": final_region,
    #     }


    def update_secret(
        self,
        secret_name: str,
        client_secret: str,
        region: Optional[str] = None,
    ) -> Dict[str, Any]:
        client, final_region = self._client(region)
        resp = client.update_secret(
            SecretId=secret_name,
            SecretString=json.dumps({"client_secret": client_secret}),
        )
        return {
            "name": resp.get("Name"),
            "arn": resp.get("ARN"),
            "version_id": resp.get("VersionId"),
            "region": final_region,
        }



    def delete_client_secret(self, org_name: str, region: Optional[str] = None) -> Dict[str, Any]:
        client, final_region = self._client(region)
        secret_name = self.build_secret_name(org_name)
        try:
            resp = client.delete_secret(
                SecretId=secret_name,
                ForceDeleteWithoutRecovery=True,
            )
            return {
                "name": resp.get("Name"),
                "arn": resp.get("ARN"),
                "deletion_date": str(resp.get("DeletionDate")),
                "region": final_region,
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return {"name": secret_name, "deleted": False, "reason": "not_found", "region": final_region}
            raise


    def list_secrets(self,region: Optional[str] = None, max_results: int = 20) -> Dict[str, Any]:
        client, final_region = self._client(region)
        resp = client.list_secrets(MaxResults=max_results)
        secrets = [
            {
                "name": s.get("Name"),
                "arn": s.get("ARN"),
                "description": s.get("Description"),
                "last_changed_date": str(s.get("LastChangedDate")),
            }
            for s in resp.get("SecretList", [])
        ]
        return {"region": final_region, "count": len(secrets), "items": secrets}


    def check_permissions(region: Optional[str] = None) -> Dict[str, Any]:
        import uuid
        session = get_boto_session()
        final_region = resolve_region(session, region)

        client = session.client("secretsmanager", region_name=final_region)
        sts = session.client("sts", region_name=final_region)
        secret_id = f"genesys/perm-check/{uuid.uuid4()}"

        checks = {
            "CreateSecret": {"allowed": False, "error": None},
            "GetSecretValue": {"allowed": False, "error": None},
            "UpdateSecret": {"allowed": False, "error": None},
            "DeleteSecret": {"allowed": False, "error": None},
        }

        caller = sts.get_caller_identity()

        try:
            client.create_secret(Name=secret_id, SecretString="temp")
            checks["CreateSecret"]["allowed"] = True
        except ClientError as e:
            checks["CreateSecret"]["error"] = e.response["Error"]["Code"]

        try:
            client.get_secret_value(SecretId=secret_id)
            checks["GetSecretValue"]["allowed"] = True
        except ClientError as e:
            checks["GetSecretValue"]["error"] = e.response["Error"]["Code"]

        try:
            client.update_secret(SecretId=secret_id, SecretString="temp-updated")
            checks["UpdateSecret"]["allowed"] = True
        except ClientError as e:
            checks["UpdateSecret"]["error"] = e.response["Error"]["Code"]

        try:
            client.delete_secret(SecretId=secret_id, ForceDeleteWithoutRecovery=True)
            checks["DeleteSecret"]["allowed"] = True
        except ClientError as e:
            checks["DeleteSecret"]["error"] = e.response["Error"]["Code"]

        return {
            "ok": all(v["allowed"] for v in checks.values()),
            "region": final_region,
            "caller_identity": caller,
            "checks": checks,
        }


    # NEW helper: create-or-update in one method
    def upsert_client_secret(
        self,
        org_name: str,
        client_secret: str,
        region: Optional[str] = None,
    ) -> Dict[str, Any]:
        secret_name = self.build_secret_name(org_name)
        try:
            return self.create_secret(secret_name=secret_name, client_secret=client_secret, region=region)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceExistsException":
                return self.update_secret(secret_name=secret_name, client_secret=client_secret, region=region)
            raise