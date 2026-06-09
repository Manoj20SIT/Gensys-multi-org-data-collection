import os
import uuid
from app.core.aws_session import get_boto_session
import boto3
from botocore.exceptions  import ClientError, NoRegionError


def check_aws_secrets_permissions(region: str | None = None) -> dict:
    # Region resolution order:
    # 1) function argument
    # 2) AWS_REGION / AWS_DEFAULT_REGION env
    # 3) boto3 session configured region (~/.aws/config, role/runtime config)
    # 4) hard fallback
    session = get_boto_session()
    
    resolved_region = (
        region
        or os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or session.region_name
        or "eu-central-1"
    )

    try:
        client = session.client("secretsmanager", region_name=resolved_region)
        sts = session.client("sts", region_name=resolved_region)
    except NoRegionError:
        # very defensive fallback
        resolved_region = "ap-northeast-1"
        client = boto3.client("secretsmanager", region_name=resolved_region)
        sts = boto3.client("sts", region_name=resolved_region)

    secret_id = f"genesys/perm-check/{uuid.uuid4()}"

    checks = {
        "CreateSecret": {"allowed": False, "error": None},
        "GetSecretValue": {"allowed": False, "error": None},
        "UpdateSecret": {"allowed": False, "error": None},
        "DeleteSecret": {"allowed": False, "error": None},
    }

    try:
        caller = sts.get_caller_identity()
    except Exception as e:
        caller = {"error": str(e)}

    try:
        client.create_secret(Name=secret_id, SecretString="temp")
        checks["CreateSecret"]["allowed"] = True
    except ClientError as e:
        checks["CreateSecret"]["error"] = e.response["Error"]["Code"]
    except Exception as e:
        checks["CreateSecret"]["error"] = str(e)

    try:
        client.get_secret_value(SecretId=secret_id)
        checks["GetSecretValue"]["allowed"] = True
    except ClientError as e:
        checks["GetSecretValue"]["error"] = e.response["Error"]["Code"]
    except Exception as e:
        checks["GetSecretValue"]["error"] = str(e)

    try:
        client.update_secret(SecretId=secret_id, SecretString="temp-updated")
        checks["UpdateSecret"]["allowed"] = True
    except ClientError as e:
        checks["UpdateSecret"]["error"] = e.response["Error"]["Code"]
    except Exception as e:
        checks["UpdateSecret"]["error"] = str(e)

    try:
        client.delete_secret(SecretId=secret_id, ForceDeleteWithoutRecovery=True)
        checks["DeleteSecret"]["allowed"] = True
    except ClientError as e:
        checks["DeleteSecret"]["error"] = e.response["Error"]["Code"]
    except Exception as e:
        checks["DeleteSecret"]["error"] = str(e)

    try:
        client.delete_secret(SecretId=secret_id, ForceDeleteWithoutRecovery=True)
        checks["DeleteSecret"]["allowed"] = True
    except ClientError as e:
        checks["DeleteSecret"]["error"] = e.response["Error"]["Code"]
    except Exception as e:
        checks["DeleteSecret"]["error"] = str(e)

    return {
        "ok": all(v["allowed"] for v in checks.values()),
        "region": region,
        "caller_identity": caller,
        "checks": checks
    }
