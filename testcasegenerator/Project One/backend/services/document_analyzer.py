"""
Document Analyzer — Extracts structured intelligence from BRD/PRD documents.
Identifies requirements, user roles, business rules, acceptance criteria,
data entities, and classifies the business domain.
"""
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("firstfintech")

# ──────────────────────────────────────────────
# Domain Classification Keywords
# ──────────────────────────────────────────────
DOMAIN_KEYWORDS = {
    "ecommerce": [
        "cart", "checkout", "product", "catalog", "shopping", "order", "shipment",
        "payment", "refund", "return", "inventory", "wishlist", "discount", "coupon",
        "pricing", "sku", "merchant", "storefront", "add to cart", "buy", "sell",
        "shipping", "delivery", "marketplace", "ecommerce", "e-commerce",
    ],
    "banking": [
        "account", "bank", "transaction", "transfer", "deposit", "withdraw",
        "balance", "loan", "interest", "credit", "debit", "atm", "cheque", "check",
        "statement", "mortgage", "fund", "kyc", "aml", "swift", "iban", "wire",
        "fintech", "payment gateway", "billing", "invoice", "ledger", "forex",
    ],
    "healthcare": [
        "patient", "doctor", "appointment", "medical", "health", "hospital",
        "prescription", "diagnosis", "treatment", "clinic", "nurse", "lab",
        "insurance", "claim", "hipaa", "ehr", "emr", "telehealth", "telemedicine",
        "pharmacy", "dosage", "vital", "symptom", "clinical",
    ],
    "education": [
        "student", "course", "enroll", "grade", "instructor", "teacher",
        "classroom", "curriculum", "exam", "assessment", "assignment", "lecture",
        "semester", "certificate", "diploma", "tuition", "scholarship", "lms",
        "learning", "training", "quiz", "syllabus",
    ],
    "logistics": [
        "shipment", "warehouse", "logistics", "freight", "cargo", "tracking",
        "route", "fleet", "supply chain", "procurement", "vendor", "dispatch",
        "manifest", "customs", "container", "pallet", "fulfillment", "3pl",
    ],
    "enterprise": [
        "workflow", "approval", "admin", "dashboard", "report", "analytics",
        "role", "permission", "audit", "compliance", "configuration", "settings",
        "notification", "integration", "api", "sso", "ldap", "active directory",
        "erp", "crm", "saas", "tenant", "organization",
    ],
}

# ──────────────────────────────────────────────
# Requirement Extraction Patterns
# ──────────────────────────────────────────────
REQUIREMENT_PATTERNS = [
    r"(?:the system|the application|the platform|the software|it)\s+(?:shall|must|should|will|needs to)\s+(.{15,200})",
    r"(?:users?|admins?|managers?|operators?)\s+(?:shall|must|should|will|can|may)\s+(?:be able to\s+)?(.{10,200})",
    r"(?:FR|NFR|REQ|BR)[\s\-]*\d+[:\s]+(.{10,300})",
    r"(?:requirement|feature|capability)[:\s]+(.{10,200})",
]

USER_ROLE_PATTERNS = [
    r"as\s+(?:a|an)\s+(\w[\w\s]{1,30}?)(?:\s*,|\s+I\s)",
    r"(?:the|a|an)\s+(\w+(?:\s+\w+)?)\s+(?:shall|must|should|will|can|may)\s+(?:be able to)?",
    r"(?:role|actor|persona|user type)[:\s]+(\w[\w\s]{1,30})",
    r"(\w+(?:\s+\w+)?)\s+permissions?",
]

BUSINESS_RULE_PATTERNS = [
    r"if\s+(.{10,150}?)\s*(?:,\s*)?then\s+(.{10,150})",
    r"when\s+(.{10,150}?)\s*(?:,\s*)?then\s+(.{10,150})",
    r"(?:business rule|rule|constraint|condition)[:\s]+(.{10,300})",
    r"(?:valid(?:ation)?|check)\s*:\s*(.{10,200})",
]

ACCEPTANCE_CRITERIA_PATTERNS = [
    r"given\s+(.{5,100}?)\s*(?:,\s*)?when\s+(.{5,100}?)\s*(?:,\s*)?then\s+(.{5,200})",
    r"(?:AC|acceptance criteria|criteria)[\s\-]*\d*[:\s]+(.{10,300})",
    r"(?:verify|confirm|ensure|validate)\s+(?:that\s+)?(.{10,200})",
]

DATA_ENTITY_PATTERNS = [
    r"(\w+(?:\s+\w+)?)\s+(?:field|column|attribute|property|parameter)",
    r"(?:field|column|attribute)[:\s]+(\w[\w\s]{1,40})",
    r"(?:enter|input|provide|specify)\s+(?:the\s+)?(\w[\w\s]{1,30}?)(?:\s+field|\s+value|\s+data)",
]

STOP_ROLES = {
    "the", "a", "an", "this", "that", "each", "every", "any", "all", "some",
    "new", "existing", "current", "valid", "invalid", "same", "other",
    "following", "specific", "particular", "relevant", "appropriate",
    "system", "application", "platform", "software", "it", "they",
}


def analyze_document(text: str) -> Dict[str, Any]:
    """
    Perform comprehensive analysis on document text.
    Returns structured intelligence for test case generation.
    """
    if not text or len(text.strip()) < 20:
        return _empty_analysis()

    text_lower = text.lower()
    words = text.split()

    analysis = {
        "domain": classify_domain(text_lower),
        "statistics": {
            "word_count": len(words),
            "line_count": text.count("\n") + 1,
            "char_count": len(text),
        },
        "requirements": extract_requirements(text),
        "user_roles": extract_user_roles(text),
        "business_rules": extract_business_rules(text),
        "acceptance_criteria": extract_acceptance_criteria(text),
        "data_entities": extract_data_entities(text),
        "sections": extract_sections(text),
        "modules": detect_modules(text),
    }

    analysis["statistics"]["requirement_count"] = len(analysis["requirements"])
    analysis["statistics"]["role_count"] = len(analysis["user_roles"])
    analysis["statistics"]["rule_count"] = len(analysis["business_rules"])
    analysis["statistics"]["module_count"] = len(analysis["modules"])

    return analysis


def classify_domain(text_lower: str) -> str:
    """Classify the document into a business domain based on keyword density."""
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        scores[domain] = score

    if not scores or max(scores.values()) == 0:
        return "generic"

    return max(scores, key=scores.get)


def extract_requirements(text: str) -> List[Dict[str, str]]:
    """Extract functional and non-functional requirements from text."""
    requirements = []
    seen = set()

    for pattern in REQUIREMENT_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            req_text = match.group(0).strip()
            # Normalize for dedup
            norm = re.sub(r"\s+", " ", req_text.lower().strip())
            if norm not in seen and len(req_text) > 15:
                seen.add(norm)
                req_type = "Non-Functional" if any(
                    kw in req_text.lower()
                    for kw in ["performance", "security", "scalab", "availab", "reliab", "usab"]
                ) else "Functional"
                requirements.append({
                    "id": f"REQ-{len(requirements)+1:03d}",
                    "text": req_text[:300],
                    "type": req_type,
                })

    # Also extract numbered/bulleted list items that look like requirements
    for match in re.finditer(r"(?m)^\s*(?:\d+[\.\)]\s*|[-•]\s+)(.{15,250})", text):
        line = match.group(1).strip()
        norm = re.sub(r"\s+", " ", line.lower())
        if norm not in seen and any(
            kw in norm for kw in ["shall", "must", "should", "allow", "enable", "support", "display", "provide", "validate"]
        ):
            seen.add(norm)
            requirements.append({
                "id": f"REQ-{len(requirements)+1:03d}",
                "text": line[:300],
                "type": "Functional",
            })

    return requirements


def extract_user_roles(text: str) -> List[str]:
    """Extract unique user roles/actors from the document."""
    roles = set()

    for pattern in USER_ROLE_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            role = match.group(1).strip().lower()
            # Clean up
            role = re.sub(r"\s+", " ", role).strip()
            words = role.split()
            if len(words) <= 3 and words[0] not in STOP_ROLES and len(role) > 2:
                roles.add(role.title())

    # Always include at least a default
    if not roles:
        roles.add("User")

    return sorted(roles)


def extract_business_rules(text: str) -> List[Dict[str, str]]:
    """Extract business rules and conditional logic."""
    rules = []
    seen = set()

    for pattern in BUSINESS_RULE_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            rule_text = match.group(0).strip()
            norm = re.sub(r"\s+", " ", rule_text.lower())
            if norm not in seen and len(rule_text) > 10:
                seen.add(norm)
                rules.append({
                    "id": f"BR-{len(rules)+1:03d}",
                    "text": rule_text[:300],
                })

    return rules


def extract_acceptance_criteria(text: str) -> List[Dict[str, str]]:
    """Extract acceptance criteria (Given/When/Then or explicit AC)."""
    criteria = []
    seen = set()

    for pattern in ACCEPTANCE_CRITERIA_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            ac_text = match.group(0).strip()
            norm = re.sub(r"\s+", " ", ac_text.lower())
            if norm not in seen and len(ac_text) > 10:
                seen.add(norm)
                criteria.append({
                    "id": f"AC-{len(criteria)+1:03d}",
                    "text": ac_text[:400],
                })

    return criteria


def extract_data_entities(text: str) -> List[str]:
    """Extract data fields and entities mentioned in the document."""
    entities = set()

    for pattern in DATA_ENTITY_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            entity = match.group(1).strip().lower()
            entity = re.sub(r"\s+", " ", entity).strip()
            if len(entity) > 2 and len(entity) < 40:
                entities.add(entity.title())

    # Common field keywords
    for kw in ["username", "password", "email", "phone", "address", "name", "date", "amount", "price", "quantity", "status", "description"]:
        if kw in text.lower():
            entities.add(kw.title())

    return sorted(entities)


def extract_sections(text: str) -> List[Dict[str, str]]:
    """Extract document section headings and hierarchy."""
    sections = []

    # Markdown headings
    for match in re.finditer(r"(?m)^(#{1,4})\s+(.+)", text):
        level = len(match.group(1))
        title = match.group(2).strip()
        sections.append({"level": level, "title": title})

    # ALL-CAPS headings
    for match in re.finditer(r"(?m)^([A-Z][A-Z\s]{4,50})$", text):
        title = match.group(1).strip()
        if not title.isdigit():
            sections.append({"level": 1, "title": title.title()})

    # Numbered section headings
    for match in re.finditer(r"(?m)^(\d+(?:\.\d+)*)\s+([A-Z].{3,80})", text):
        number = match.group(1)
        title = match.group(2).strip()
        level = number.count(".") + 1
        sections.append({"level": level, "title": title})

    return sections


def detect_modules(text: str) -> List[str]:
    """Detect functional modules/features mentioned in the document."""
    module_keywords = [
        "authentication", "authorization", "login", "registration", "signup",
        "dashboard", "reporting", "analytics", "notifications", "messaging",
        "payment", "billing", "invoicing", "subscription",
        "user management", "profile", "settings", "configuration",
        "search", "filtering", "sorting",
        "import", "export", "integration",
        "workflow", "approval", "review",
        "audit", "logging", "monitoring",
        "file upload", "document management",
    ]

    text_lower = text.lower()
    found = []
    for mod in module_keywords:
        if mod in text_lower:
            found.append(mod.title())

    return sorted(set(found))


def _empty_analysis() -> Dict[str, Any]:
    return {
        "domain": "generic",
        "statistics": {"word_count": 0, "line_count": 0, "char_count": 0,
                       "requirement_count": 0, "role_count": 0, "rule_count": 0, "module_count": 0},
        "requirements": [],
        "user_roles": ["User"],
        "business_rules": [],
        "acceptance_criteria": [],
        "data_entities": [],
        "sections": [],
        "modules": [],
    }
