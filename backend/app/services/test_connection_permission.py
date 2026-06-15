import re
from typing import Any, Dict, List


def extract_permissions_from_raw_error(raw_error: Any) -> List[str]:
    if not raw_error:
        return []

    if isinstance(raw_error, dict):
        text = str(raw_error.get("message", ""))
    else:
        text = str(raw_error)

    # Correct regex: extract content inside [ ... ]
    groups = re.findall(r'\[(.*?)\]', text)
    print(f"the groups is ={groups}")
    perms: List[str] = []
    for g in groups:
        for p in g.split(","):   # handles [perm1, perm2]
            p = p.strip()
            if p and ":" in p:
                perms.append(p)

    return sorted(set(perms))
    # perms: List[str] = []
    # for g in groups:
    #     for p in g.split(","):
    #         p = p.strip()
    #         if p and ":" in p:
    #             perms.append(p)

    # return groups

def build_permission_summary(
    checks: List[Dict[str, Any]],
    missing_areas: List[str] | None = None
) -> Dict[str, Any]:
    """
    Build user-facing summary:
    {
      "success": bool,
      "missingAreas": [...],
      "permissions_required": { area: [perm1, perm2] }
    }
    """
    permissions_required: Dict[str, List[str]] = {}

    for c in checks or []:
        # only forbidden checks
        if c.get("status") != "forbidden":
            continue

        area = c.get("key")
        perms = extract_permissions_from_raw_error(c.get("raw_error"))

        if area:
            permissions_required.setdefault(area, [])
            permissions_required[area].extend(perms)

    # unique+sorted
    for area in list(permissions_required.keys()):
        permissions_required[area] = sorted(set(permissions_required[area]))
        # remove empty entries
        if not permissions_required[area]:
            permissions_required.pop(area)

    merged_areas = sorted(set((missing_areas or []) + list(permissions_required.keys())))
    success = len(merged_areas) == 0

    return {
        "success": success,
        "missingAreas": merged_areas,
        "permissions_required": permissions_required
    }