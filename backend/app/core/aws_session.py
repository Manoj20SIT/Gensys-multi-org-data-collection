import os
import boto3

def get_boto_session():
    app_env = (os.getenv("APP_ENV") or "").lower()
    profile = (os.getenv("AWS_PROFILE") or os.getenv("AWS_DEFAULT_PROFILE") or "").strip()

    if app_env == "dev" and profile:
        return boto3.session.Session(profile_name=profile)

    return boto3.session.Session()

def resolve_region(session: boto3.session.Session, region: str | None = None) -> str:
    return (
        region
        or os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or session.region_name
        or "ap-northeast-1"
    )
