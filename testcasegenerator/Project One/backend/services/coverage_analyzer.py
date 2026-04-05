"""
Coverage Analyzer — Maps test cases to requirements and identifies gaps.
Calculates coverage by requirement, module, user role, and priority.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger("firstfintech")


def analyze_coverage(
    test_cases: List[Dict[str, Any]],
    analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze test coverage by comparing generated test cases against
    the document analysis results.
    """
    requirements = analysis.get("requirements", [])
    roles = analysis.get("user_roles", [])
    modules = analysis.get("modules", [])
    domain = analysis.get("domain", "generic")

    # ── Requirement Coverage ──
    req_ids = {r["id"] for r in requirements}
    covered_req_ids = set()
    for tc in test_cases:
        rid = tc.get("requirement_id", "")
        if rid and rid in req_ids:
            covered_req_ids.add(rid)

    req_coverage_pct = (len(covered_req_ids) / len(req_ids) * 100) if req_ids else 100.0
    uncovered_reqs = [r for r in requirements if r["id"] not in covered_req_ids]

    # ── Test Type Distribution ──
    type_dist = {}
    for tc in test_cases:
        tt = tc.get("test_type", "Functional")
        type_dist[tt] = type_dist.get(tt, 0) + 1

    # ── Priority Distribution ──
    priority_dist = {}
    for tc in test_cases:
        p = tc.get("priority", "Medium")
        priority_dist[p] = priority_dist.get(p, 0) + 1

    # ── Role Coverage ──
    covered_roles = set()
    for tc in test_cases:
        role = tc.get("user_role", "")
        if role:
            covered_roles.add(role)
        for tag in tc.get("tags", []):
            if tag in roles:
                covered_roles.add(tag)

    role_coverage_pct = (len(covered_roles) / len(roles) * 100) if roles else 100.0

    # ── Module Coverage ──
    tc_text_blob = " ".join(tc.get("title", "") + " " + tc.get("steps", "") for tc in test_cases).lower()
    covered_modules = [m for m in modules if m.lower() in tc_text_blob]
    module_coverage_pct = (len(covered_modules) / len(modules) * 100) if modules else 100.0
    uncovered_modules = [m for m in modules if m not in covered_modules]

    # ── Suggested Additional Tests ──
    suggestions = []
    for req in uncovered_reqs:
        suggestions.append({
            "reason": f"Uncovered requirement: {req['id']}",
            "description": req["text"][:150],
            "suggested_type": "Functional",
            "priority": "High",
        })
    for mod in uncovered_modules:
        suggestions.append({
            "reason": f"Uncovered module: {mod}",
            "description": f"No test cases cover the {mod} module. Add functional and negative tests.",
            "suggested_type": "Functional",
            "priority": "Medium",
        })

    return {
        "total_test_cases": len(test_cases),
        "domain": domain,
        "requirement_coverage": {
            "total_requirements": len(requirements),
            "covered": len(covered_req_ids),
            "uncovered": len(uncovered_reqs),
            "coverage_percentage": round(req_coverage_pct, 1),
        },
        "role_coverage": {
            "total_roles": len(roles),
            "covered_roles": sorted(covered_roles),
            "coverage_percentage": round(role_coverage_pct, 1),
        },
        "module_coverage": {
            "total_modules": len(modules),
            "covered_modules": covered_modules,
            "uncovered_modules": uncovered_modules,
            "coverage_percentage": round(module_coverage_pct, 1),
        },
        "test_type_distribution": type_dist,
        "priority_distribution": priority_dist,
        "suggestions": suggestions[:10],
        "overall_coverage_percentage": round(
            (req_coverage_pct + role_coverage_pct + module_coverage_pct) / 3, 1
        ),
    }
