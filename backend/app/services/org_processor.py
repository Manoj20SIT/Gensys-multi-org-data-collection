# import asyncio
# import logging
# from typing import List
# from app.models.schemas import OrgCredentials, OrgRunResult
# from app.services.genesys_client import GenesysClient

# logger = logging.getLogger(__name__)

# class OrgProcessor:
#     """
#     Controls concurrency with semaphore.
#     If worker_pool_size=2, only 2 orgs run concurrently.
#     3rd waits until one slot is free.
#     """

#     def __init__(self, genesys_client: GenesysClient, worker_pool_size: int = 2):
#         self.genesys_client = genesys_client
#         self.semaphore = asyncio.Semaphore(worker_pool_size)

#     async def _process_one_org(self, org: OrgCredentials) -> OrgRunResult:
#         async with self.semaphore:
#             if not org.active:
#                 return OrgRunResult(org.org_name, org.account_id, "SKIPPED", "org inactive")

#             try:
#                 # Step-1 token fetched implicitly by client call
#                 # Step-2 test call using token
#                 resp = await self.genesys_client.get_org_me(org)

#                 if resp.status_code == 401:
#                     return OrgRunResult(org.org_name, org.account_id, "CREDENTIAL_ERROR", "401 after refresh retry")

#                 resp.raise_for_status()
#                 return OrgRunResult(org.org_name, org.account_id, "SUCCESS", "token fetched and API call success")

#             except Exception as ex:
#                 logger.exception("org processing failed: %s", org.org_name)
#                 return OrgRunResult(org.org_name, org.account_id, "FAILED", str(ex))

#     async def run(self, orgs: List[OrgCredentials]) -> List[OrgRunResult]:
#         tasks = [self._process_one_org(org) for org in orgs]
#         return await asyncio.gather(*tasks)
