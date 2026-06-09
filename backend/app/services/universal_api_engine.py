
"""
FLOW OVERVIEW
=============
Route: /run
   -> CollectionService.run(interval)
      -> For each org:
         -> Build ApiTask list (task_factory)
         -> UniversalApiExecutor.execute_task(org, task)
            -> token_service.get_token(org)
            -> create_genesys_client(token, org.api_base_url)
            -> dynamic API class + method invocation
            -> if 401: invalidate token, refresh, retry once
            -> if 403: raise AppException with clear context
            -> extractor parses response into usable value
         -> aggregate all task outputs
         -> map to final UI response fields

Design goals:
- One common executor for all Genesys APIs
- Reusable across different apis but for new field you need to add the extarctor like inbound call count , agent assist etc   analytics/users/groups/billing etc 
- Easy debug through detailed logs
"""

from dataclasses import dataclass
import json
from typing import Any, Dict, Callable, List, Optional

from PureCloudPlatformClientV2.apis.analytics_api import AnalyticsApi
from PureCloudPlatformClientV2.apis.users_api import UsersApi
from PureCloudPlatformClientV2.apis.groups_api import GroupsApi
from PureCloudPlatformClientV2.apis.organization_api import OrganizationApi
from PureCloudPlatformClientV2.rest import ApiException
from app.core.logger import logger
from app.core.exceptions import TaskExecutionException
# Add billing api class if available in your SDK version
from PureCloudPlatformClientV2.apis.billing_api import BillingApi
from PureCloudPlatformClientV2.apis.agent_assistants_api import AgentAssistantsApi
from PureCloudPlatformClientV2.apis.knowledge_api import KnowledgeApi
from PureCloudPlatformClientV2.apis.workforce_management_api import WorkforceManagementApi
from PureCloudPlatformClientV2.apis.recording_api import RecordingApi
from PureCloudPlatformClientV2.apis.quality_api import QualityApi
from PureCloudPlatformClientV2.apis.speech_text_analytics_api import SpeechTextAnalyticsApi
from PureCloudPlatformClientV2.apis.learning_api import LearningApi
from PureCloudPlatformClientV2.apis.coaching_api import CoachingApi
from PureCloudPlatformClientV2.apis.gamification_api import GamificationApi



API_MAP = {
    "AnalyticsApi": AnalyticsApi,
    "UsersApi": UsersApi,
    "GroupsApi": GroupsApi,
    "OrganizationApi": OrganizationApi,
    "BillingApi": BillingApi,
    "AgentAssistantsApi": AgentAssistantsApi,
    "KnowledgeApi":KnowledgeApi,
    "WorkforceManagementApi":WorkforceManagementApi,
    "RecordingApi":RecordingApi,
    "QualityApi":QualityApi,
    "SpeechTextAnalyticsApi":SpeechTextAnalyticsApi,
    "LearningApi":LearningApi,
    "CoachingApi":CoachingApi,
    "GamificationApi":GamificationApi
    
}


@dataclass
class ApiTask:
    # Output key under which task result will be stored
    key: str
    # API class key from API_MAP
    api_name: str
    # Method name on SDK API class
    method_name: str
    # kwargs sent directly to SDK method (body/query/path params)
    kwargs: Dict[str, Any]
    # Optional extractor key
    extractor: Optional[str] = None
    # Optional extractor arguments
    extractor_args: Optional[Dict[str, Any]] = None



class UniversalApiEngine:
    def __init__(self):
        self.extractors: Dict[str, Callable[..., Any]] = {
            "raw": self._raw,
            "analytics_total_metric": self._sum_metric_from_results,
            "analytics_grouped_metric": self._group_and_sum_metric_from_results,
            "entity_count": self._entity_count,
            "recording_activation_status":self._recording_activation,
            "sta_activation_status":self._sta_activation
        }
        logger.info(
            "UniversalApiEngine initialized | apis=%s | extractors=%s",
            list(API_MAP.keys()),
            list(self.extractors.keys())
        )





    def execute_task(self, api_client, task: ApiTask, org_name: str = "unknown"):
        """
        Executes one dynamic API task:
        1) Resolve API class
        2) Resolve method
        3) Execute call
        4) Apply extractor (optional)
        """
        logger.info(
            f"Task start | key={task.key} | api= {task.api_name} | method={task.method_name}"
        )

        try:
            # Validate API registration
            if task.api_name not in API_MAP:
                logger.error(f"Task failed | key={task.key} | unknown api_name={task.api_name}")
                raise ValueError(f"Unknown api_name: {task.api_name}")

            # Build API object from provided shared api_client
            api_cls = API_MAP[task.api_name]
            api_obj = api_cls(api_client)

            # Validate method existence
            if not hasattr(api_obj, task.method_name):
                logger.error(
                    "Task failed | key=%s | method not found | api=%s | method=%s",
                    task.key, task.api_name, task.method_name
                )
                raise AttributeError(f"Method '{task.method_name}' not found in '{task.api_name}'")

            fn = getattr(api_obj, task.method_name)

            # Perform SDK call
            logger.debug(f"Executing SDK call | key= {task.key} | kwargs={task.kwargs}")
            resp = fn(**task.kwargs)
            # print(f" receieved result is =================== {resp}")
            logger.info(f"SDK call success | key={task.key}")
            # Print raw API response object
            logger.info(f"\n[{org_name}] API RESPONSE | task={task.key} | api={task.api_name}.{task.method_name}")
            # logger.info(resp)

            # If no extractor configured, return raw SDK response
            if not task.extractor:
                logger.debug(f"No extractor configured | key={task.key} | returning raw response")
                return resp

            # Validate extractor registration
            if task.extractor not in self.extractors:
                logger.error(f"Task failed | key={task.key} | unknown extractor= {task.extractor}")
                raise ValueError(f"Unknown extractor: {task.extractor}")

            # Apply extractor
            extractor_fn = self.extractors[task.extractor]
            logger.debug(
                f"Applying extractor | key={task.key} | extractor={task.extractor} | extractor_args={task.extractor_args}"
                
            )
            value = extractor_fn(resp, **(task.extractor_args or {}))
            logger.info(f"Task completed | key={task.key}")
            return value
        
        except ApiException as e:
            
            status = getattr(e, "status", None)
            reason = getattr(e, "reason", None)
            body = getattr(e, "body", None)
            context_id = self._extract_context_id(body)
            retryable = status in [429, 500, 502, 503, 504]

            logger.error(
                f"Genesys API exception | org={org_name} | key={task.key} | "
                f"api={task.api_name} | method={task.method_name} | "
                f"status={status} | reason={reason} | contextId={context_id}",
                exc_info=True
            )

            raise TaskExecutionException(
                message=f"Genesys API call failed: {reason or 'ApiException'}",
                task_key=task.key,
                api=task.api_name,
                method=task.method_name,
                status=status,
                reason=reason,
                context_id=context_id,
                retryable=retryable,
                context={"raw_body": body}
            )

        except Exception as e:
            logger.error(
    f"Unexpected task exception | org={org_name} | key={task.key} | "
    f"api={task.api_name} | method={task.method_name} | error={str(e)}",
    exc_info=True)
            raise


    def _extract_context_id(self, error_body):
        """Best-effort parse of Genesys contextId from error body JSON."""
        try:
            if not error_body:
                return None
            data = json.loads(error_body) if isinstance(error_body, str) else error_body
            return data.get("contextId")
        except Exception:
            return None





    def run_tasks(self, api_client, tasks: List[ApiTask] ,org_name: str = "unknown") -> Dict[str, Any]:
        """
        Executes all tasks sequentially and returns dictionary:
        {
          task.key: extracted_value,
          ...
        }
        """
        logger.info(f"Run tasks started | task_count={len(tasks)}" )
        out: Dict[str, Any] = {}
        task_errors: List[Dict[str, Any]] = []

        for idx, t in enumerate(tasks, start=1):
            logger.info(f"Processing task {idx}/{len(tasks)} | key={t.key}")
            try:
                out[t.key] = self.execute_task(api_client, t, org_name=org_name)
            except TaskExecutionException as e:
                out[t.key] = None
                task_errors.append(e.to_dict())
                logger.error(
                    f"Task failed but continuing | org={org_name} | key={t.key} | "
                    f"status={e.context.get('status')} | reason={e.context.get('reason')}"
                )

            except Exception as e:
                logger.error(
                    f"Task failed but continuing | org={org_name} | key={t.key} | "
                    f"api={t.api_name} | method={t.method_name} | error={str(e)}",
                    exc_info=True
                )
                out[t.key] = None
                task_errors.append({
                    "task_key": t.key,
                    "api": t.api_name,
                    "method": t.method_name,
                    "error": str(e)
                })

        logger.info("Run tasks completed successfully")
        return {
        "data": out,
        "task_errors": task_errors
    }

    # ---------------- extractors ----------------

    
    def _raw(self, resp, **_):
        
        """Return response object as-is."""
        return resp

    def _entity_count(self, resp, **_):
        """
        Generic list count extractor.
        Works for APIs returning response.entities list.
        """
        count = len(getattr(resp, "entities", None) or [])
        logger.debug(f"Extractor entity_count result={count}")
        return count

    def _sum_metric_from_results(self, resp, metric_name: str, stat_field: str = "count", **_):
        """
        Sum one analytics metric over all results/data buckets.
        Example: metric_name='nOffered', stat_field='count'
        """
        total = 0.0
        for r in (getattr(resp, "results", None) or []):
            for d in (getattr(r, "data", None) or []):
                for m in (getattr(d, "metrics", None) or []):
                    if getattr(m, "metric", None) == metric_name:
                        stats = getattr(m, "stats", None)
                        if stats:
                            val = getattr(stats, stat_field, None)
                            if val is not None:
                                total += float(val)
        
        logger.debug(
            "Extractor analytics_total_metric | metric=%s | stat_field=%s | total=%s",
            metric_name, stat_field, total
        )
        return total

    def _group_and_sum_metric_from_results(self, resp, metric_name: str, group_key: str, stat_field: str = "count", **_):
        """
        Group analytics metric by one dimension key.
        Example output: {'inbound': 120, 'outbound': 40}
        """
        grouped: Dict[str, float] = {}
        for r in (getattr(resp, "results", None) or []):
            group = getattr(r, "group", None) or {}
            k = group.get(group_key)
            if not k:
                continue
            grouped.setdefault(k, 0.0)

            for d in (getattr(r, "data", None) or []):
                for m in (getattr(d, "metrics", None) or []):
                    if getattr(m, "metric", None) == metric_name:
                        stats = getattr(m, "stats", None)
                        if stats:
                            val = getattr(stats, stat_field, None)
                            if val is not None:
                                grouped[k] += float(val)
        
        logger.debug(
            "Extractor analytics_grouped_metric | metric=%s | group_key=%s | stat_field=%s | grouped=%s",
            metric_name, group_key, stat_field, grouped
        )
        return grouped
    
    def _recording_activation(self, resp, **_):
        """
        Active if recording settings response is present/non-empty.
        """
        if resp is None:
            return "inactive"

        # If SDK model/object exists, treat as active
        # If dict-like response, ensure non-empty
        if isinstance(resp, dict):
            return "active" if len(resp) > 0 else "inactive"

        return "active"
    
    def _sta_activation(self, resp, **_):
        """
        returns active when textanalytics is enabled or else incative 
        """
        if not isinstance(resp,dict):
            return "inactive"
        return "active" if resp.get("textAnalyticsEnabled") is True else "inactive"
    
    
