from typing import Dict, Any, List, Optional
from app.core.logger import logger

def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def map_to_ui_fields(raw: Dict[str, Any], fields: Optional[List[str]] = None,
                     billing_metrics: Optional[Dict[str, Any]] = None
                     ) -> Dict[str, Any]:
    raw = raw or {}
    billing_metrics = billing_metrics or {}
    logger.info("map_to_ui_fields start | raw_keys=%d billing_keys=%d",
                    len(raw.keys()), len(billing_metrics.keys()))
    by_dir_offered = raw.get("voice_by_direction_offered") or {}
    by_dir_out = raw.get("voice_by_direction_outbound_attempted") or {}
    by_media = raw.get("offered_by_media") or {}
    by_msg = raw.get("message_offered_by_type") or {}
    bot_by_media = raw.get("bot_offered_by_media") or {}

    inbound = _to_float(by_dir_offered.get("inbound"))
    outbound = _to_float(by_dir_out.get("outbound"))

    t_handle_sum = _to_float(raw.get("voice_thandle_sum"))
    n_connected = _to_float(raw.get("voice_nconnected_count"))

    n_abandon = _to_float(raw.get("voice_inbound_nabandon"))
    n_offered_inbound = _to_float(raw.get("voice_inbound_noffered"))
    agent_assist_status = "enabled" if (raw.get("agent_assist_count") or 0) > 0 else "disabled"
    knowledge_base_status="active" if (raw.get("knowledge_base_count") or 0) > 0 else "inactive"
    wfm_activation_status="active" if (raw.get("wfm_activation_count") or 0) > 0 else "inactive"
    qm_activation_status="active" if (raw.get("qm_activation_count") or 0) > 0 else "inactive"
    survey_activation_status="active" if (raw.get("survey_activation_count") or 0) > 0 else "inactive"
    learning_activation_status="active" if (raw.get("learning_activation_count") or 0) > 0 else "inactive"
    gamification_activation_status= "active" if (raw.get("gamification_activation_count") or 0) > 0 else "inactive"
    # recording_activation_status= "active" if (raw.get("recording_activation__count") or 0) > 0 else "inactive"

    license_model = billing_metrics.get("licenseModel") or {}
    ai_tokens = billing_metrics.get("aiExperienceTokens") or {}
    
    
    logger.info(f"raw keys:{list(raw.keys())}")
    logger.info(f"sta_activation_status value {raw.get('sta_activation_status')}")
    
    
    
    metrics ={
        
        "inbound_call_count": inbound,
        "outbound_call_count": outbound,
        "total_call_count": inbound + outbound,

        "email_count": _to_float(by_media.get("email")),
        "chat_count": _to_float(by_media.get("chat")),

        "sms_conversations": _to_float(by_msg.get("sms")),
        "social_count": _to_float(by_msg.get("social")),
        "open_messages": _to_float(by_msg.get("open")),
        "web_messaging": _to_float(by_msg.get("webmessaging")),

        "native_voice_bot": _to_float(bot_by_media.get("voice")),
        "native_chatbot_sessions": _to_float(bot_by_media.get("chat")) + _to_float(bot_by_media.get("message")),

        "avg_call_duration": (t_handle_sum / n_connected) if n_connected else 0.0,
        "call_abandonment_rate": (n_abandon / n_offered_inbound) if n_offered_inbound else 0.0,

        "gpr_used": 0.0,
        "gpe_event_count": 0.0,
        "users_page_count": _to_int(raw.get("users_page_count")),
        "groups_page_count": _to_int(raw.get("groups_page_count")),
        "agent_assist": agent_assist_status,
        "knowledge":knowledge_base_status,
        "wfm_activation":wfm_activation_status,
        "recording_activation":raw.get("recording_activation_status"),
        "qm_activation":qm_activation_status,
        "survey_activation":survey_activation_status,
        "sta_activation":raw.get("sta_activation_status") or "unknown",
        "learning_activation":learning_activation_status,
        "gamification_activation":gamification_activation_status,
        # billing fields
        "isInRampPeriod": billing_metrics.get("isInRampPeriod"),
        "licenseModel": (billing_metrics.get("licenseModel") or {}).get("license_model"),
        # "userCommit": (billing_metrics.get("licenseModel") or {}).get("user_commit"),
        # "userCount": (billing_metrics.get("licenseModel") or {}).get("user_count"),
        "seatAdoptionBucket": (billing_metrics.get("licenseModel") or {}).get("seat_adoption_bucket"),
        # "tokenCommited": (billing_metrics.get("aiExperienceTokens") or {}).get("token_commited"),
        # "tokenActual": (billing_metrics.get("aiExperienceTokens") or {}).get("token_actual"),
        
        

        "userCommit": _to_float(license_model.get("user_commit")),
        "userCount": _to_float(license_model.get("user_count")),
        "tokenCommited": _to_float(ai_tokens.get("token_commited")),
        "tokenActual": _to_float(ai_tokens.get("token_actual")),

        
        
    }
    # If no specific fields requested, return all
    if not fields:
        return metrics

    # Return only requested fields (that exist in metrics)
    return {f: metrics.get(f) for f in fields if f in metrics}