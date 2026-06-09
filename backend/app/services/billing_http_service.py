from datetime import datetime
import requests
from app.core.logger import logger



def interval_end_to_epoch_ms(interval: str) -> int:
    """
    Input:
      2026-05-01T00:00:00.000Z/2026-05-01T23:59:59.999Z
    Output:
      epoch milliseconds of interval end time
    """
    try:
        end_iso = interval.split("/")[1]
        dt = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1000)
    except Exception as e:
        raise ValueError(f"Invalid interval format: {interval}. Expected ISO/ISO. Error: {e}")


def fetch_billing_subscription_overview_http(org, access_token: str, interval: str):
    """
    org must have:
      - org.org_name
      - org.api_base_url
      - org.client_id
      - org.client_secret

    token_service must provide:
      - get_token(org, force_refresh=False)
      - invalidate(org_name)
    """
    # access_token = access_token
    api_host = org.api_base_url.rstrip("/")

    period_ending_ts = interval_end_to_epoch_ms(interval)
    url = f"{api_host}/api/v2/billing/subscriptionoverview?periodEndingTimestamp={period_ending_ts}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=30)

        # # Retry once if token expired
        # if resp.status_code == 401:
        #     logger.warning(f"401 for org={org.org_name}. Refreshing token and retrying once.")
        #     access_token.invalidate(org.org_name)
        #     new_token = token_service.get_token(org, force_refresh=True)
        #     headers["Authorization"] = f"Bearer {new_token}"
        #     resp = requests.get(url, headers=headers, timeout=30)

        try:
            data = resp.json()
            
        except Exception:
            data = {"raw": resp.text}

        logger.info(
            f"Billing overview HTTP org={org.org_name} status={resp.status_code} url={url}"
        )
        return resp.status_code, data

    except requests.RequestException as e:
        logger.error(f"Billing request failed for org={org.org_name}: {e}")
        return 500, {"error": f"Request failed: {str(e)}"}