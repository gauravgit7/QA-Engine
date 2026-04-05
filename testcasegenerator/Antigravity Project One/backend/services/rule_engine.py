"""
Advanced Multi-Pass Rule Engine — Generates 50-100+ professional UAT test cases.

Pass 1: Scenario Identification — match document against pattern library
Pass 2: Scenario Expansion — generate detailed steps with test data
Pass 3: Variation & Edge Cases — add negative, boundary, security variants
"""
import re
import logging
from typing import List, Dict, Any, Optional
from faker import Faker

from services.document_analyzer import analyze_document
from services.pattern_library import get_matching_patterns

fake = Faker()
logger = logging.getLogger("firstfintech")


# ──────────────────────────────────────────────
# Test Data Generation
# ──────────────────────────────────────────────

def _gen_data(entities: List[str], variant: str = "valid") -> str:
    """Generate realistic test data string based on detected entities."""
    parts = []
    for e in entities[:5]:
        el = e.lower()
        if variant == "valid":
            if "email" in el:
                parts.append(f"Email: {fake.email()}")
            elif "phone" in el or "mobile" in el:
                parts.append(f"Phone: {fake.phone_number()}")
            elif "date" in el or "time" in el:
                parts.append(f"Date: {fake.date_between('+1d', '+30d').strftime('%Y-%m-%d')}")
            elif "name" in el:
                parts.append(f"Name: {fake.name()}")
            elif "amount" in el or "price" in el:
                parts.append(f"Amount: ${fake.pydecimal(left_digits=4, right_digits=2, positive=True)}")
            elif "address" in el:
                parts.append(f"Address: {fake.address().replace(chr(10), ', ')}")
            elif "password" in el:
                parts.append(f"Password: {fake.password(length=12)}")
            elif "username" in el:
                parts.append(f"Username: {fake.user_name()}")
            elif "description" in el:
                parts.append(f"Description: {fake.sentence()}")
            elif "status" in el:
                parts.append(f"Status: Active")
            elif "quantity" in el:
                parts.append(f"Quantity: {fake.random_int(1, 100)}")
            else:
                parts.append(f"{e}: {fake.word()}")
        elif variant == "invalid":
            if "email" in el:
                parts.append(f"Email: not-an-email")
            elif "phone" in el or "mobile" in el:
                parts.append(f"Phone: abc")
            elif "date" in el:
                parts.append(f"Date: 31/13/2099")
            elif "amount" in el or "price" in el:
                parts.append(f"Amount: -999")
            elif "password" in el:
                parts.append(f"Password: 123")
            else:
                parts.append(f"{e}: (empty)")
        elif variant == "boundary":
            if "email" in el:
                parts.append(f"Email: {'a'*200}@test.com")
            elif "name" in el:
                parts.append(f"Name: {'A'*255}")
            elif "amount" in el or "price" in el:
                parts.append(f"Amount: $999999999.99")
            else:
                parts.append(f"{e}: {'X'*255}")
    return ", ".join(parts) if parts else "N/A"


# ──────────────────────────────────────────────
# Variation Generators (Pass 3)
# ──────────────────────────────────────────────

def _make_negative_variant(tc: Dict, actor: str, entities: List[str]) -> Dict:
    """Create a negative test variant from a positive test case."""
    return {
        "title": tc["title"].replace("Verify successful", "Verify failure on invalid").replace("Verify ", "Verify error handling for "),
        "steps": tc["steps"].replace("valid data", "invalid/missing data").replace("Enter valid", "Enter invalid"),
        "expected": "System rejects the action with appropriate error message. No invalid data persisted.",
        "test_type": "Negative",
        "priority": "High",
        "tags": tc.get("tags", []) + ["Negative"],
        "duration": tc.get("duration", 120),
        "test_data": _gen_data(entities, "invalid"),
    }


def _make_boundary_variant(tc: Dict, entities: List[str]) -> Dict:
    """Create a boundary/edge case variant."""
    return {
        "title": f"Verify boundary conditions for: {tc['title'][:80]}",
        "steps": "1. Enter data at maximum/minimum allowed limits.\n2. Submit and observe system behavior.",
        "expected": "System handles boundary values correctly — either accepts or shows clear boundary error.",
        "test_type": "Edge",
        "priority": "Medium",
        "tags": tc.get("tags", []) + ["BoundaryValue"],
        "duration": 90,
        "test_data": _gen_data(entities, "boundary"),
    }


def _make_security_variant(tc: Dict, actor: str) -> Dict:
    """Create a security test variant."""
    return {
        "title": f"Verify access control for: {tc['title'][:80]}",
        "steps": f"1. Log in as unauthorized {actor}.\n2. Attempt to perform the action.\n3. Attempt via direct URL/API.",
        "expected": "Access denied. Feature not visible or disabled. Server-side authorization enforced.",
        "test_type": "Security",
        "priority": "High",
        "tags": tc.get("tags", []) + ["Security", "RBAC"],
        "duration": 120,
        "test_data": "N/A",
    }


def _make_performance_variant(tc: Dict) -> Dict:
    """Create a performance test variant."""
    return {
        "title": f"Verify performance under load for: {tc['title'][:70]}",
        "steps": "1. Execute the operation with 100+ concurrent users.\n2. Measure response time.\n3. Check for errors.",
        "expected": "Response time within SLA (< 3 seconds). No errors under concurrent load.",
        "test_type": "Performance",
        "priority": "Low",
        "tags": tc.get("tags", []) + ["Performance", "Load"],
        "duration": 300,
        "test_data": "N/A",
    }


# ──────────────────────────────────────────────
# Requirement-Based Scenario Generators
# ──────────────────────────────────────────────

def _generate_from_requirement(req: Dict, idx: int, actor: str, entities: List[str]) -> List[Dict]:
    """Generate test cases from a single extracted requirement."""
    req_text = req["text"]
    cases = []

    # Happy path
    cases.append({
        "title": f"Verify: {req_text[:100]}",
        "steps": f"1. Log in as {actor}.\n2. Navigate to the relevant module.\n3. Perform the described action with valid data.\n4. Verify outcome.",
        "expected": f"System fulfills the requirement: {req_text[:120]}",
        "test_type": "Positive",
        "priority": "High",
        "tags": ["Requirement", req.get("type", "Functional")],
        "duration": 120,
        "test_data": _gen_data(entities, "valid"),
        "requirement_id": req["id"],
    })

    # Negative variant
    cases.append({
        "title": f"Verify failure scenario for: {req_text[:90]}",
        "steps": f"1. Log in as {actor}.\n2. Attempt the action with invalid/missing inputs.\n3. Observe error handling.",
        "expected": "System prevents invalid operation. Clear error message displayed. Data integrity maintained.",
        "test_type": "Negative",
        "priority": "High",
        "tags": ["Requirement", "Negative"],
        "duration": 90,
        "test_data": _gen_data(entities, "invalid"),
        "requirement_id": req["id"],
    })

    return cases


def _generate_from_business_rule(rule: Dict, idx: int, actor: str) -> List[Dict]:
    """Generate test cases from a business rule."""
    return [{
        "title": f"Verify business rule: {rule['text'][:100]}",
        "steps": f"1. Set up conditions matching the rule.\n2. Execute the triggering action as {actor}.\n3. Verify the expected outcome.",
        "expected": f"Business rule enforced correctly: {rule['text'][:120]}",
        "test_type": "Positive",
        "priority": "High",
        "tags": ["BusinessRule"],
        "duration": 150,
        "test_data": "N/A",
        "requirement_id": rule["id"],
    }, {
        "title": f"Verify business rule violation handling: {rule['text'][:80]}",
        "steps": f"1. Set up conditions that violate the rule.\n2. Attempt the action.\n3. Observe enforcement.",
        "expected": "System prevents rule violation. Appropriate error or block applied.",
        "test_type": "Negative",
        "priority": "High",
        "tags": ["BusinessRule", "Negative"],
        "duration": 120,
        "test_data": "N/A",
        "requirement_id": rule["id"],
    }]


def _generate_from_acceptance_criteria(ac: Dict, idx: int, actor: str) -> Dict:
    """Generate a test case from an acceptance criterion."""
    return {
        "title": f"Verify acceptance criteria: {ac['text'][:100]}",
        "steps": f"1. Log in as {actor}.\n2. Set up the given preconditions.\n3. Execute the when action.\n4. Verify the then outcome.",
        "expected": f"Acceptance criteria met: {ac['text'][:120]}",
        "test_type": "Positive",
        "priority": "High",
        "tags": ["AcceptanceCriteria"],
        "duration": 120,
        "test_data": "N/A",
        "requirement_id": ac["id"],
    }


def _generate_role_access_tests(roles: List[str]) -> List[Dict]:
    """Generate role-based access tests for each detected user role."""
    cases = []
    for role in roles[:6]:
        cases.append({
            "title": f"Verify {role} can access authorized features",
            "steps": f"1. Log in as {role}.\n2. Navigate through all accessible modules.\n3. Verify feature availability.",
            "expected": f"{role} can access all features authorized for this role. No unauthorized features visible.",
            "test_type": "Positive",
            "priority": "High",
            "tags": ["RBAC", role],
            "duration": 180,
            "test_data": f"Role: {role}, Credentials: test_{role.lower().replace(' ', '_')}@test.com",
        })
        cases.append({
            "title": f"Verify {role} cannot access unauthorized features",
            "steps": f"1. Log in as {role}.\n2. Attempt to access features restricted from this role.\n3. Try direct URL access.",
            "expected": f"Restricted features hidden or disabled for {role}. Direct URL access returns 403.",
            "test_type": "Security",
            "priority": "High",
            "tags": ["RBAC", "Security", role],
            "duration": 120,
            "test_data": "N/A",
        })
    return cases


def _generate_e2e_scenarios(domain: str, modules: List[str], actor: str) -> List[Dict]:
    """Generate end-to-end workflow tests based on detected modules."""
    cases = []
    if len(modules) >= 2:
        module_chain = " → ".join(modules[:5])
        cases.append({
            "title": f"End-to-End: Complete {domain.title()} workflow through {module_chain}",
            "steps": "\n".join([f"{i+1}. Complete actions in {mod} module." for i, mod in enumerate(modules[:5])]),
            "expected": f"Complete workflow executes successfully across all modules. Data consistent throughout.",
            "test_type": "Positive",
            "priority": "High",
            "tags": ["E2E", "Workflow", domain.title()],
            "duration": 600,
            "test_data": "N/A",
        })
        cases.append({
            "title": f"End-to-End: Verify data integrity across {module_chain}",
            "steps": f"1. Create data in first module.\n2. Process through intermediate modules.\n3. Verify in final module.",
            "expected": "Data remains consistent and accurate across all module boundaries.",
            "test_type": "Positive",
            "priority": "High",
            "tags": ["E2E", "DataIntegrity"],
            "duration": 480,
            "test_data": "N/A",
        })
    return cases


# ══════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT — Multi-Pass Generation
# ══════════════════════════════════════════════════════════════

def generate_cases_from_story(text: str, base_id: Optional[str] = "TC-UAT",
                               options: Optional[Dict] = None) -> List[dict]:
    """
    Multi-pass UAT test case generation engine.
    Generates 50-100+ test cases from BRD/PRD document text.
    """
    options = options or {}
    target_count = options.get("test_case_count", 50)
    include_negative = options.get("include_negative", True)
    include_edge = options.get("include_edge", True)
    base_id = base_id or "TC-UAT"

    # ── Analyze Document ──
    analysis = analyze_document(text)
    domain = analysis["domain"]
    requirements = analysis["requirements"]
    roles = analysis["user_roles"]
    rules = analysis["business_rules"]
    criteria = analysis["acceptance_criteria"]
    entities = analysis["data_entities"]
    modules = analysis["modules"]
    primary_actor = roles[0] if roles else "User"

    logger.info(f"Document Analysis: domain={domain}, reqs={len(requirements)}, roles={len(roles)}, rules={len(rules)}, modules={len(modules)}")

    all_cases: List[Dict] = []

    # ══════════════════════════════════
    # PASS 1 — Scenario Identification
    # ══════════════════════════════════

    # 1a. Pattern library matches
    matched_patterns = get_matching_patterns(text.lower(), domain)
    logger.info(f"Pass 1: {len(matched_patterns)} patterns matched from library")
    for p in matched_patterns:
        all_cases.append({
            "title": p["title"],
            "steps": p["steps"],
            "expected": p["expected"],
            "test_type": p.get("test_type", "Positive"),
            "priority": p.get("priority", "Medium"),
            "tags": p.get("tags", []),
            "duration": p.get("duration", 120),
            "test_data": _gen_data(entities, "valid") if p.get("test_type") == "Positive" else "N/A",
        })

    # 1b. Requirement-based scenarios
    for i, req in enumerate(requirements):
        all_cases.extend(_generate_from_requirement(req, i, primary_actor, entities))

    # 1c. Business rule scenarios
    for i, rule in enumerate(rules):
        all_cases.extend(_generate_from_business_rule(rule, i, primary_actor))

    # 1d. Acceptance criteria scenarios
    for i, ac in enumerate(criteria):
        all_cases.append(_generate_from_acceptance_criteria(ac, i, primary_actor))

    logger.info(f"Pass 1 complete: {len(all_cases)} base scenarios identified")

    # ══════════════════════════════════
    # PASS 2 — Expand with Role & E2E
    # ══════════════════════════════════

    # Role-based access tests
    all_cases.extend(_generate_role_access_tests(roles))

    # End-to-end workflow tests
    all_cases.extend(_generate_e2e_scenarios(domain, modules, primary_actor))

    logger.info(f"Pass 2 complete: {len(all_cases)} scenarios after role & E2E expansion")

    # ══════════════════════════════════
    # PASS 3 — Variations & Edge Cases
    # ══════════════════════════════════

    positive_cases = [c for c in all_cases if c.get("test_type") == "Positive"]

    if include_negative:
        for tc in positive_cases[:15]:
            all_cases.append(_make_negative_variant(tc, primary_actor, entities))

    if include_edge:
        for tc in positive_cases[:8]:
            all_cases.append(_make_boundary_variant(tc, entities))

    # Security variants for high-priority positives
    for tc in positive_cases[:5]:
        all_cases.append(_make_security_variant(tc, primary_actor))

    # Performance variants for key scenarios
    for tc in positive_cases[:3]:
        all_cases.append(_make_performance_variant(tc))

    logger.info(f"Pass 3 complete: {len(all_cases)} total scenarios after variations")

    # ══════════════════════════════════
    # FINALIZE — Deduplicate, format, trim
    # ══════════════════════════════════

    # Deduplicate by title
    seen_titles = set()
    unique_cases = []
    for tc in all_cases:
        title_norm = tc["title"].lower().strip()
        if title_norm not in seen_titles:
            seen_titles.add(title_norm)
            unique_cases.append(tc)

    # Trim to target count
    final_cases = unique_cases[:target_count]

    # Format output
    result = []
    for i, tc in enumerate(final_cases):
        result.append({
            "id": f"{base_id}-{str(i+1).zfill(3)}",
            "title": tc["title"],
            "preconditions": tc.get("preconditions", f"{primary_actor} is authenticated and has required permissions."),
            "steps": tc["steps"],
            "expectedResult": tc["expected"],
            "priority": tc.get("priority", "Medium"),
            "test_type": tc.get("test_type", "Functional"),
            "test_data": tc.get("test_data", "N/A"),
            "postconditions": tc.get("postconditions", "System state is consistent. Audit log updated."),
            "tags": tc.get("tags", []),
            "estimated_duration": tc.get("duration", 120),
            "business_context": tc.get("business_context", f"Validates {domain} business requirement for {primary_actor} role."),
            "user_role": tc.get("user_role", primary_actor),
            "requirement_id": tc.get("requirement_id", ""),
        })

    logger.info(f"Final output: {len(result)} UAT test cases generated for domain={domain}")
    return result
