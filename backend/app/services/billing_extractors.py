from typing import Dict, Any, Optional


def _to_float(v, default=0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default

def extract_is_in_ramp_period(mapped_billing: Dict[str, Any]) -> Optional[bool]:
    return mapped_billing.get("isInRampPeriod")


def extract_license_model(mapped_billing: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect license model from usage names containing 'Genesys Cloud CX'
    and return normalized seat adoption metrics.

    user_commit = prepayQuantity
    user_count  = usageQuantity
    seat_adoption_bucket = (user_count / user_commit) * 100
    """
    usage_by_name = mapped_billing.get("usage_by_name", {}) or {}

    cx_candidates = []
    for name, obj in usage_by_name.items():
        if "genesys cloud cx" in name.lower():
            cx_candidates.append((name, obj))
            
    if not cx_candidates:
        return {
            "matched_name": None,
            "license_model": "unknown",
            "user_commit": 0.0,
            "user_count": 0.0,
            "seat_adoption_bucket": "0%",
            "unit_of_measure_type":None
            
        }

    matched_name, usage_obj = cx_candidates[0]
    name_lower = matched_name.lower()
    print(f"License name matched 8888888888888888888888888......................: {matched_name}")

    if "concurrent" in name_lower:
        license_model = matched_name
    elif "hourly" in name_lower:
        license_model = matched_name
    elif "named" in name_lower or "configured" in name_lower:
        license_model = matched_name
    else:
        license_model = matched_name

    user_commit = _to_float(usage_obj.get("prepayQuantity"))   # commit
    user_count = _to_float(usage_obj.get("usageQuantity"))     # actual used
    unit_of_measure_type = usage_obj.get("unitOfMeasureType")

    if user_commit > 0:
        adoption_pct = (user_count / user_commit) * 100.0
    else:
        adoption_pct = 0.0

    return {
        "matched_name": matched_name,
        "license_model": license_model,
        "user_commit": user_commit,
        "user_count": user_count,
        "seat_adoption_bucket": round(adoption_pct, 2),
        "unit_of_measure_type":unit_of_measure_type
    }
    
    

def extract_ai_experience_tokens(mapped_billing: Dict[str, Any]) -> Dict[str, Any]:
    """
    Find usage entry whose name contains 'AI Experience Tokens' (partial match).

    Mapping requested:
      token_commited = usageQuantity
      token_actual   = prepayQuantity
    """
    usage_by_name = mapped_billing.get("usage_by_name", {}) or {}

    matched_name = None
    matched_obj = None

    for name, obj in usage_by_name.items():
        if "ai experience tokens" in name.lower():
            matched_name = name
            matched_obj = obj
            break

    if not matched_obj:
        return {
            "matched_name": None,
            "token_commited": 0.0,
            "token_actual": 0.0
        }

    return {
        "matched_name": matched_name,
        "token_commited": _to_float(matched_obj.get("usageQuantity")),
        "token_actual": _to_float(matched_obj.get("prepayQuantity"))
    }
