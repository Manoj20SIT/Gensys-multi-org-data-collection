
"""
FLOW OVERVIEW (Task Factory)
============================
This module is responsible for building a list of ApiTask objects
that UniversalApiEngine will execute.

Route /run -> CollectionService.run(interval) ->
   genesys_apitasks(interval) [this file] ->
      returns list[ApiTask] ->
         UniversalApiEngine.run_tasks(...) executes each task.

Why this file exists:
- Keep query definitions separate from execution logic
- Easy to add/remove metrics in one place
- Reusable pattern for analytics/users/groups/billing tasks
"""

from typing import List, Optional, Set

from app.core.logger import logger
from app.services.universal_api_engine import ApiTask


def pred(dimension: str, value: str):
    """
    Build one analytics dimension predicate.
    Example:
    pred("mediaType", "voice")
    """
    return {"type": "dimension", "dimension": dimension, "operator": "matches", "value": value}


def and_filter(*predicates):
    
    
    """
    Build analytics filter in standard format:
    {
      "type": "and",
      "clauses": [
        {"type": "or", "predicates": [ ... ]},
        ...
      ]
    }

    Note:
    - Empty predicates are ignored
    - This keeps task definitions clean
    """
    return {"type": "and", "clauses": [{"type": "or", "predicates": [p]} for p in predicates if p]}


from datetime import datetime

def _interval_end_to_epoch_ms(interval: str) -> int:
    # interval format: "start/end"
    end_iso = interval.split("/")[1]
    dt = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)


def genesys_apitasks(interval: str, required_task_keys: Optional[Set[str]] = None) -> List[ApiTask]:
    
    """
    Build all analytics + sample non-analytics tasks.

    Current coverage:
    - inbound/outbound voice counts
    - email/chat
    - message channel splits
    - bot sessions
    - avg call duration inputs
    - abandonment inputs
    - sample users/groups count (to prove dynamic engine)

    Returns:
        List[ApiTask]
    """
    
    if not interval or "/" not in interval:
        logger.warning(f"genesys_apitasks called with unexpected interval format: {interval}")

    logger.info(f"Building analytics tasks | interval= {interval} ")
    tasks: List[ApiTask] = []

     # ---------------------------------------------------------------------
    # 1) Voice by direction
    #    - inbound_call_count comes from nOffered where direction=inbound
    #    - outbound_call_count comes from nOutboundAttempted where direction=outbound
    # ---------------------------------------------------------------------
    
    tasks.append(ApiTask(
        key="voice_by_direction_offered",
        api_name="AnalyticsApi",
        method_name="post_analytics_conversations_aggregates_query",
        kwargs={"body": {
            "interval": interval,
            "groupBy": ["direction"],
            "metrics": ["nOffered"],
            "filter": and_filter(pred("mediaType", "voice"))
        }},
        extractor="analytics_grouped_metric",
        extractor_args={"metric_name": "nOffered", "group_key": "direction", "stat_field": "count"}
    ))

    
    tasks.append(ApiTask(
        key="voice_by_direction_outbound_attempted",
        api_name="AnalyticsApi",
        method_name="post_analytics_conversations_aggregates_query",
        kwargs={"body": {
            "interval": interval,
            "groupBy": ["direction"],
            "metrics": ["nOutboundAttempted"],
            "filter": and_filter(pred("mediaType", "voice"))
        }},
        extractor="analytics_grouped_metric",
        extractor_args={"metric_name": "nOutboundAttempted", "group_key": "direction", "stat_field": "count"}
    ))

# ---------------------------------------------------------------------
    # 2) Offered count by mediaType
    #    - email_count, chat_count are extracted from this single task
    # ---------------------------------------------------------------------
    tasks.append(ApiTask(
        key="offered_by_media",
        api_name="AnalyticsApi",
        method_name="post_analytics_conversations_aggregates_query",
        kwargs={"body": {
            "interval": interval,
            "groupBy": ["mediaType"],
            "metrics": ["nOffered"]
        }},
        extractor="analytics_grouped_metric",
        extractor_args={"metric_name": "nOffered", "group_key": "mediaType", "stat_field": "count"}
    ))

     # ---------------------------------------------------------------------
    # 3) Offered message count by messageType
    #    - sms/social/open/webmessaging from one query
    # ---------------------------------------------------------------------
    tasks.append(ApiTask(
        key="message_offered_by_type",
        api_name="AnalyticsApi",
        method_name="post_analytics_conversations_aggregates_query",
        kwargs={"body": {
            "interval": interval,
            "groupBy": ["messageType"],
            "metrics": ["nOffered"],
            "filter": and_filter(pred("mediaType", "message"))
        }},
        extractor="analytics_grouped_metric",
        extractor_args={"metric_name": "nOffered", "group_key": "messageType", "stat_field": "count"}
    ))

 # ---------------------------------------------------------------------
    # 4) Bot offered by mediaType
    #    - native_voice_bot from mediaType=voice
    #    - native_chatbot_sessions from mediaType=chat/message
    # ---------------------------------------------------------------------
    # tasks.append(ApiTask(
    #     key="bot_offered_by_media",
    #     api_name="AnalyticsApi",
    #     method_name="post_analytics_conversations_aggregates_query",
    #     kwargs={"body": {
    #         "interval": interval,
    #         "groupBy": ["mediaType"],
    #         "metrics": ["nOffered"],
    #         "filter": and_filter(pred("participantType", "bot"))
    #     }},
    #     extractor="analytics_grouped_metric",
    #     extractor_args={"metric_name": "nOffered", "group_key": "mediaType", "stat_field": "count"}
    # ))

    # ---------------------------------------------------------------------
    # 5) Average call duration inputs
    #    avg_call_duration = tHandle(sum) / nConnected(count)
    # ---------------------------------------------------------------------
    tasks.append(ApiTask(
        key="voice_thandle_sum",
        api_name="AnalyticsApi",
        method_name="post_analytics_conversations_aggregates_query",
        kwargs={"body": {
            "interval": interval,
            "metrics": ["tHandle"],
            "filter": and_filter(pred("mediaType", "voice"))
        }},
        extractor="analytics_total_metric",
        extractor_args={"metric_name": "tHandle", "stat_field": "sum"}
    ))

    tasks.append(ApiTask(
        key="voice_nconnected_count",
        api_name="AnalyticsApi",
        method_name="post_analytics_conversations_aggregates_query",
        kwargs={"body": {
            "interval": interval,
            "metrics": ["nConnected"],
            "filter": and_filter(pred("mediaType", "voice"))
        }},
        extractor="analytics_total_metric",
        extractor_args={"metric_name": "nConnected", "stat_field": "count"}
    ))

    # ---------------------------------------------------------------------
    # 6) Abandonment inputs (inbound voice)
    #    call_abandonment_rate = nAbandon / nOffered
    # ---------------------------------------------------------------------
    tasks.append(ApiTask(
        key="voice_inbound_nabandon",
        api_name="AnalyticsApi",
        method_name="post_analytics_conversations_aggregates_query",
        kwargs={"body": {
            "interval": interval,
            "metrics": ["nAbandon"],
            "filter": and_filter(pred("mediaType", "voice"), pred("direction", "inbound"))
        }},
        extractor="analytics_total_metric",
        extractor_args={"metric_name": "nAbandon", "stat_field": "count"}
    ))

    tasks.append(ApiTask(
        key="voice_inbound_noffered",
        api_name="AnalyticsApi",
        method_name="post_analytics_conversations_aggregates_query",
        kwargs={"body": {
            "interval": interval,
            "metrics": ["nOffered"],
            "filter": and_filter(pred("mediaType", "voice"), pred("direction", "inbound"))
        }},
        extractor="analytics_total_metric",
        extractor_args={"metric_name": "nOffered", "stat_field": "count"}
    ))

    # optional: users/groups examples (dynamic engine proof)
    tasks.append(ApiTask(
        key="users_page_count",
        api_name="UsersApi",
        method_name="get_users",
        kwargs={"page_size": 100, "page_number": 1},
        extractor="entity_count"
    ))

    tasks.append(ApiTask(
        key="groups_page_count",
        api_name="GroupsApi",
        method_name="get_groups",
        kwargs={"page_size": 100, "page_number": 1},
        extractor="entity_count"
    ))
    
    period_ending_timestamp = _interval_end_to_epoch_ms(interval)

    # tasks.append(
    #     ApiTask(
    #         key="billing_subscription_overview",
    #         api_name="BillingApi",
    #         method_name="get_billing_subscriptionoverview",  # verify in your SDK
    #         kwargs={"period_ending_timestamp": period_ending_timestamp},
    #         extractor=None
    #     )
    # )
    # agent assist count
    tasks.append(ApiTask(
    key="agent_assist_count",
    api_name="AgentAssistantsApi",
    method_name="get_assistants",
    kwargs={},  # optional; small payload
    extractor="entity_count"                     # returns len(entities)
))
    
    # Knowledge field
    tasks.append(ApiTask(
    key="knowledge_base_count",
    api_name="KnowledgeApi",
    method_name="get_knowledge_knowledgebases",
    kwargs={},  # optional; small payload
    extractor="entity_count"                    # returns len(entities)
))
    # wfm activation fields 
    tasks.append(ApiTask(
    key="wfm_activation_count",
    api_name="WorkforceManagementApi",
    method_name="get_workforcemanagement_managementunits",
    kwargs={},  # optional; small payload
    extractor="entity_count"                    # returns len(entities)
))
    
    # Recording activation field
    tasks.append(ApiTask(
    key="recording_activation_status",
    api_name="RecordingApi",
    method_name="get_recording_settings",
    kwargs={},  # optional; small payload
    extractor="recording_activation_status"                    # returns len(entities)
))
    # QM activation field 
    tasks.append(ApiTask(
    key="qm_activation_count",
    api_name="QualityApi",
    method_name="get_quality_forms_evaluations",
    kwargs={},  # optional; small payload
    extractor="entity_count"                    # returns len(entities)
))
    # survery activation field
    tasks.append(ApiTask(
    key="survey_activation_count",
    api_name="QualityApi",
    method_name="get_quality_forms_surveys",
    kwargs={},  # optional; small payload
    extractor="entity_count"                    # returns len(entities)
))
    
    # sta activation field
    tasks.append(ApiTask(
    key="sta_activation_status",
    api_name="SpeechTextAnalyticsApi",
    method_name="get_speechandtextanalytics_settings",
    kwargs={},  # optional; small payload
    extractor="sta_activation_status"                    # returns len(entities)
))
    
    # learning activation field
    tasks.append(ApiTask(
    key="learning_activation_count",
    api_name="LearningApi",
    method_name="get_learning_modules",
    kwargs={},  # optional; small payload
    extractor="entity_count"                    # returns len(entities)
))
  
#   # coaching activation field
#     tasks.append(ApiTask(
#     key="learning_activation_count",
#     api_name="LearningApi",
#     method_name="get_learning_modules",
#     kwargs={},  # optional; small payload
#     extractor="entity_count"                    # returns len(entities)
# ))

  # gamification activation field
    tasks.append(ApiTask(
    key="gamification_activation_count",
    api_name="GamificationApi",
    method_name="get_gamification_profiles",
    kwargs={},  # optional; small payload
    extractor="entity_count"                    # returns len(entities)
))
  

    if required_task_keys:
        tasks = [t for t in tasks if t.key in required_task_keys]
    return tasks
