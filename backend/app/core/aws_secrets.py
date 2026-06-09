import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import APP_ENV,settings
from app.core.logger import logger


def get_aws_session() -> boto3.Session:
    """
    One code path for both dev and prod.
    boto3 default credential chain handles:
    - dev: AWS_PROFILE / local aws config / env creds
    - prod: IAM role
    """
    return boto3.Session(region_name=settings.AWS_REGION)


def aws_startup_check(max_results: int = 5) -> None:
    try:
        session = get_aws_session()

        logger.info("Running AWS startup check...")
        logger.info(f"App Env          : {APP_ENV}")
        logger.info(f"AWS Region       : {settings.AWS_REGION}")

        # 1) Who am I?
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        logger.info(f"AWS Account      : {identity.get('Account')}")
        logger.info(f"AWS ARN          : {identity.get('Arn')}")

        # 2) Can I access Secrets Manager?
        sm = session.client("secretsmanager")
        resp = sm.list_secrets(MaxResults=max_results)
        secrets = resp.get("SecretList", [])

        if not secrets:
            logger.info("No secrets found.")
        else:
            logger.info(f"Secrets preview (max {max_results}):")
            for s in secrets:
                logger.info(f" - {s.get('Name')}")

        logger.success("AWS startup check passed")

    except (BotoCoreError, ClientError, Exception) as e:
        logger.exception(f"AWS startup check failed: {e}")
        raise
