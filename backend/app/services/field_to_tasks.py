from typing import List, Optional, Set, Dict

ALLOWED_FIELDS = {
    "inbound_call_count", "outbound_call_count", "total_call_count",
    "email_count", "chat_count",
    "sms_conversations", "social_count", "open_messages", "web_messaging",
    "native_voice_bot", "native_chatbot_sessions",
    "avg_call_duration", "call_abandonment_rate",
    "gpr_used", "gpe_event_count",
    "users_page_count", "groups_page_count", "agent_assist_count","knowledge_base_count",
    "wfm_activation" ,"recording_activation","qm_activation" , "survey_activation" ,"sta_activation",
    "learning_activation" ,"gamification_activation"
}

FIELD_TO_TASKS: Dict[str, Set[str]] = {
    "inbound_call_count": {"voice_by_direction_offered"},
    "outbound_call_count": {"voice_by_direction_outbound_attempted"},
    "total_call_count": {"voice_by_direction_offered", "voice_by_direction_outbound_attempted"},
    "email_count": {"offered_by_media"},
    "chat_count": {"offered_by_media"},
    "sms_conversations": {"message_offered_by_type"},
    "social_count": {"message_offered_by_type"},
    "open_messages": {"message_offered_by_type"},
    "web_messaging": {"message_offered_by_type"},
    "native_voice_bot": {"bot_offered_by_media"},
    "native_chatbot_sessions": {"bot_offered_by_media"},
    "avg_call_duration": {"voice_thandle_sum", "voice_nconnected_count"},
    "call_abandonment_rate": {"voice_inbound_nabandon", "voice_inbound_noffered"},
    "users_page_count": {"users_page_count"},
    "groups_page_count": {"groups_page_count"},
    "gpr_used": set(),
    "gpe_event_count": set(),
    "agent_assist":{"agent_assist_count"},
    "knowledge":{"knowledge_base_count"},
    "wfm_activation":{"wfm_activation_count"},
    "recording_activation":{"recording_activation_status"},
    "qm_activation":{"qm_activation_count"},
    "survey_activation":{"survey_activation_count"},
    "sta_activation":{"sta_activation_status"},
    "learning_activation":{"learning_activation_count"},
    "gamification_activation":{"gamification_activation_count"}
}

def _filter_metrics(metrics: dict, fields: Optional[List[str]]) -> dict:
    if not fields:
        return metrics
    return {f: metrics.get(f) for f in fields if f in metrics}
