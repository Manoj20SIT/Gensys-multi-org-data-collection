from datetime import datetime, timedelta, timezone
from typing import List, Optional, Set

from app.services.universal_api_engine import ApiTask


def _last_5m_interval() -> str:
    end = datetime.now(timezone.utc).replace(microsecond=0)
    start = end - timedelta(minutes=5)
    return f"{start.isoformat().replace('+00:00','Z')}/{end.isoformat().replace('+00:00','Z')}"


def _interval_end_to_epoch_ms(interval: str) -> int:
    end_iso = interval.split("/")[1]
    dt = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)


def build_permission_probe_tasks(required_keys: Optional[Set[str]] = None) -> List[ApiTask]:
    interval = _last_5m_interval()
    period_ending_timestamp = _interval_end_to_epoch_ms(interval)

    tasks: List[ApiTask] = [
        ApiTask(
            key="analytics",
            api_name="AnalyticsApi",
            method_name="post_analytics_conversations_aggregates_query",
            kwargs={"body": {"interval": interval, "metrics": ["nOffered"]}},
            extractor=None
        ),
        ApiTask(
            key="users",
            api_name="UsersApi",
            method_name="get_users",
            kwargs={"page_size": 1, "page_number": 1},
            extractor=None
        ),
        ApiTask(
            key="groups",
            api_name="GroupsApi",
            method_name="get_groups",
            kwargs={"page_size": 1, "page_number": 1},
            extractor=None
        ),
        ApiTask(
            key="agent_assist",
            api_name="AgentAssistantsApi",
            method_name="get_assistants",
            kwargs={},
            extractor=None
        ),
        ApiTask(
            key="knowledge",
            api_name="KnowledgeApi",
            method_name="get_knowledge_knowledgebases",
            kwargs={},
            extractor=None
        ),
        ApiTask(
            key="wfm",
            api_name="WorkforceManagementApi",
            method_name="get_workforcemanagement_managementunits",
            kwargs={},
            extractor=None
        ),
        ApiTask(
            key="recording",
            api_name="RecordingApi",
            method_name="get_recording_settings",
            kwargs={},
            extractor=None
        ),
        ApiTask(
            key="qm",
            api_name="QualityApi",
            method_name="get_quality_forms_evaluations",
            kwargs={},
            extractor=None
        ),
        ApiTask(
            key="survey",
            api_name="QualityApi",
            method_name="get_quality_forms_surveys",
            kwargs={},
            extractor=None
        ),
        ApiTask(
            key="sta",
            api_name="SpeechTextAnalyticsApi",
            method_name="get_speechandtextanalytics_settings",
            kwargs={},
            extractor=None
        ),
        ApiTask(
            key="learning",
            api_name="LearningApi",
            method_name="get_learning_modules",
            kwargs={},
            extractor=None
        ),
        ApiTask(
            key="gamification",
            api_name="GamificationApi",
            method_name="get_gamification_profiles",
            kwargs={},
            extractor=None
        ),
        # Billing probe via SDK (if available in your SDK version)
        # ApiTask(
        #     key="billing",
        #     api_name="BillingApi",
        #     method_name="get_billing_subscriptionoverview",
        #     kwargs={"period_ending_timestamp": period_ending_timestamp},
        #     extractor=None
        # ),
    ]

    if required_keys:
        tasks = [t for t in tasks if t.key in required_keys]

    return tasks
