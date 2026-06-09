def build_usage_name_map(billing_data: dict) -> dict:
    usage_map = {}
    for item in billing_data.get("usages", []) or []:
        name = item.get("name")
        if name:
            usage_map[name] = item
    print(f"the ne data formta for biling is {usage_map} ")
    return usage_map


def map_billing_data(billing_data: dict) -> dict:
    """
    billing_data is the raw JSON returned from billing endpoint.
    Returns transformed object with usage map + raw.
    """
    
    return {
        # "raw": billing_data,
        "usage_by_name": build_usage_name_map(billing_data),
        "isInRampPeriod": billing_data.get("isInRampPeriod")
    }
