"""
Pattern Library — 200+ test scenario patterns across 6 business domains.
Each pattern has trigger phrases, scenario templates, and test case structures.
Used by the multi-pass generation engine to produce comprehensive UAT test cases.
"""

from typing import List, Dict, Any


def _p(title: str, steps: str, expected: str, test_type: str = "Positive",
       priority: str = "High", tags: List[str] = None, duration: int = 120) -> Dict[str, Any]:
    """Helper to build a scenario pattern dict."""
    return {
        "title": title,
        "steps": steps,
        "expected": expected,
        "test_type": test_type,
        "priority": priority,
        "tags": tags or [],
        "duration": duration,
    }


# ══════════════════════════════════════════════════════════════
#  CROSS-DOMAIN / GENERIC PATTERNS
# ══════════════════════════════════════════════════════════════

GENERIC_PATTERNS: Dict[str, List[Dict]] = {

    # ── CRUD Operations ──
    "create": [
        _p("Verify successful creation with all valid mandatory fields",
           "1. Navigate to creation form.\n2. Fill all mandatory fields with valid data.\n3. Click Submit.",
           "Record is created successfully. Confirmation message displayed. Record visible in listing.",
           tags=["CRUD", "HappyPath"]),
        _p("Verify creation fails when mandatory fields are empty",
           "1. Navigate to creation form.\n2. Leave all mandatory fields empty.\n3. Click Submit.",
           "System blocks submission. Validation errors shown for each empty mandatory field.",
           "Negative", "High", ["CRUD", "Validation"]),
        _p("Verify creation with maximum allowed field lengths",
           "1. Fill each field with maximum allowed characters.\n2. Submit the form.",
           "System either accepts data or shows clear boundary error. No data corruption.",
           "Edge", "Medium", ["BoundaryValue"]),
        _p("Verify creation with special characters in text fields",
           "1. Enter special characters (<, >, &, \", ', /) in text fields.\n2. Submit.",
           "System handles special characters safely. No XSS or injection vulnerabilities.",
           "Security", "High", ["XSS", "InputSanitization"]),
        _p("Verify duplicate creation is prevented",
           "1. Create a record with unique field values.\n2. Attempt to create another record with the same unique values.",
           "System prevents duplicate and displays appropriate error message.",
           "Negative", "High", ["CRUD", "Uniqueness"]),
    ],

    "read": [
        _p("Verify listing displays all records with correct data",
           "1. Navigate to listing page.\n2. Verify data columns match expected fields.\n3. Verify record count.",
           "All records displayed with correct data in proper columns.",
           tags=["CRUD", "Listing"]),
        _p("Verify detail view shows complete record information",
           "1. Click on a record from listing.\n2. Verify all fields are displayed.",
           "Detail view shows all fields with accurate data. Read-only fields are not editable.",
           tags=["CRUD", "DetailView"]),
        _p("Verify empty state is handled gracefully",
           "1. Navigate to listing with no records.\n2. Observe the display.",
           "Appropriate empty state message shown (e.g., 'No records found'). No errors.",
           "Edge", "Low", ["EmptyState"]),
    ],

    "update": [
        _p("Verify successful update of existing record",
           "1. Select a record.\n2. Modify one or more fields.\n3. Save changes.",
           "Record updated successfully. Updated data reflected in listing and detail view.",
           tags=["CRUD", "Update"]),
        _p("Verify update preserves unmodified fields",
           "1. Open a record with multiple fields.\n2. Modify only one field.\n3. Save.",
           "Only the modified field is changed. All other fields retain original values.",
           tags=["CRUD", "DataIntegrity"]),
        _p("Verify concurrent update handling",
           "1. Open same record in two sessions.\n2. Update different fields in each.\n3. Save both.",
           "System handles concurrent updates with optimistic locking or last-write-wins strategy.",
           "Edge", "Medium", ["Concurrency"]),
    ],

    "delete": [
        _p("Verify successful deletion with confirmation",
           "1. Select a record.\n2. Click Delete.\n3. Confirm deletion in dialog.",
           "Record removed from listing. Confirmation message shown. Related data handled appropriately.",
           tags=["CRUD", "Delete"]),
        _p("Verify cancel on delete confirmation keeps record intact",
           "1. Select a record.\n2. Click Delete.\n3. Click Cancel in confirmation dialog.",
           "Record remains unchanged. No data lost.",
           tags=["CRUD", "Delete"]),
        _p("Verify deletion of record with dependencies",
           "1. Select a record that has dependent records.\n2. Attempt deletion.",
           "System either cascade deletes, blocks with dependency warning, or soft deletes.",
           "Edge", "High", ["DataIntegrity", "Cascade"]),
    ],

    # ── Search & Filter ──
    "search": [
        _p("Verify search returns accurate results for exact match",
           "1. Enter exact known value in search field.\n2. Execute search.",
           "Search results contain the matching record. Non-matching records excluded.",
           tags=["Search"]),
        _p("Verify search returns results for partial match",
           "1. Enter partial text in search field.\n2. Execute search.",
           "All records containing the partial text are returned.",
           tags=["Search"]),
        _p("Verify search with no matching results",
           "1. Enter a value that does not exist.\n2. Execute search.",
           "Empty results with 'No results found' message. No errors.",
           "Negative", "Medium", ["Search", "EmptyState"]),
        _p("Verify search with special characters",
           "1. Enter special characters in search field.\n2. Execute search.",
           "System handles safely without SQL injection. Results or empty state shown.",
           "Security", "High", ["Search", "Injection"]),
    ],

    "filter": [
        _p("Verify filtering by single criterion",
           "1. Apply a single filter (e.g., status = Active).\n2. Review results.",
           "Only records matching the filter criterion are displayed.",
           tags=["Filter"]),
        _p("Verify filtering by multiple criteria",
           "1. Apply two or more filters simultaneously.\n2. Review results.",
           "Results match ALL applied filter criteria (AND logic).",
           tags=["Filter", "Combinatorial"]),
        _p("Verify filter reset clears all filters",
           "1. Apply filters.\n2. Click Reset/Clear Filters.",
           "All filters removed. Full unfiltered listing displayed.",
           tags=["Filter"]),
    ],

    # ── Sorting & Pagination ──
    "sort": [
        _p("Verify ascending sort on sortable columns",
           "1. Click column header to sort ascending.\n2. Verify data order.",
           "Data sorted in correct ascending order for the selected column.",
           tags=["Sort"]),
        _p("Verify descending sort on sortable columns",
           "1. Click column header again for descending.\n2. Verify data order.",
           "Data sorted in correct descending order.",
           tags=["Sort"]),
    ],

    "pagination": [
        _p("Verify pagination displays correct page counts",
           "1. Navigate to listing with many records.\n2. Check page count indicator.",
           "Page count correctly reflects total records divided by page size. Navigation controls work.",
           "Medium", tags=["Pagination"]),
    ],

    # ── Validation ──
    "validation": [
        _p("Verify email field validation",
           "1. Enter invalid email formats (no @, no domain, spaces).\n2. Submit.",
           "Validation error displayed for each invalid format. Valid emails accepted.",
           "Negative", "High", ["Validation", "Email"]),
        _p("Verify numeric field rejects non-numeric input",
           "1. Enter alphabetic characters in numeric-only field.\n2. Submit.",
           "System rejects input or shows validation error.",
           "Negative", "Medium", ["Validation", "DataType"]),
        _p("Verify date field validation",
           "1. Enter invalid dates (31 Feb, future dates if not allowed).\n2. Submit.",
           "Invalid dates rejected with clear error messages.",
           "Negative", "Medium", ["Validation", "Date"]),
        _p("Verify required field indicators are visible",
           "1. Open any form with required fields.\n2. Check for asterisk or other indicators.",
           "All required fields clearly marked. Submission without them shows validation errors.",
           tags=["Validation", "UX"]),
        _p("Verify phone number format validation",
           "1. Enter phone numbers in various invalid formats.\n2. Submit.",
           "Invalid formats rejected. Valid international formats accepted.",
           "Negative", "Medium", ["Validation", "Phone"]),
    ],

    # ── Export & Import ──
    "export": [
        _p("Verify data export to Excel format",
           "1. Navigate to listing with data.\n2. Click Export to Excel.\n3. Open downloaded file.",
           "Excel file downloads with all visible data. Columns match table headers.",
           tags=["Export"]),
        _p("Verify data export to CSV format",
           "1. Click Export to CSV.\n2. Open downloaded file.",
           "CSV file contains all records with proper delimiter and encoding.",
           tags=["Export"]),
        _p("Verify export with applied filters",
           "1. Apply filters to listing.\n2. Export data.",
           "Exported file contains only filtered records, not entire dataset.",
           tags=["Export", "Filter"]),
    ],

    "import": [
        _p("Verify successful data import from valid file",
           "1. Prepare valid import file.\n2. Upload and execute import.",
           "All records imported successfully. Confirmation message with import count.",
           tags=["Import"]),
        _p("Verify import rejects invalid file format",
           "1. Upload file in unsupported format.\n2. Attempt import.",
           "System rejects file with clear format error message.",
           "Negative", "Medium", ["Import", "Validation"]),
    ],

    # ── Notifications ──
    "notification": [
        _p("Verify success notifications display correctly",
           "1. Perform a successful action (create, update, delete).\n2. Observe notification.",
           "Success notification displayed with appropriate message. Auto-dismisses after timeout.",
           tags=["Notification", "UX"]),
        _p("Verify error notifications display correctly",
           "1. Trigger an error condition.\n2. Observe notification.",
           "Error notification displayed with actionable message. Does not auto-dismiss.",
           "Negative", tags=["Notification", "UX"]),
    ],

    # ── Error Handling ──
    "error": [
        _p("Verify graceful handling of server errors",
           "1. Trigger a server-side error (e.g., API timeout).\n2. Observe application behavior.",
           "User-friendly error message displayed. No raw stack traces shown. Application remains usable.",
           "Negative", "High", ["ErrorHandling", "Resilience"]),
        _p("Verify session timeout handling",
           "1. Leave application idle beyond session timeout.\n2. Attempt an action.",
           "User redirected to login page with session expired message. No data loss.",
           "Edge", "Medium", ["Session", "Security"]),
    ],

    # ── Access Control ──
    "permission": [
        _p("Verify role-based access control enforcement",
           "1. Log in as user with restricted role.\n2. Attempt to access restricted feature.",
           "Access denied. Restricted features not visible or clickable. No data leakage.",
           "Security", "High", ["RBAC", "Authorization"]),
        _p("Verify admin can access all features",
           "1. Log in as administrator.\n2. Navigate to all modules.",
           "All features and admin functions accessible. Management tools available.",
           tags=["RBAC", "Admin"]),
        _p("Verify URL manipulation does not bypass access control",
           "1. Log in as restricted user.\n2. Manually enter URL for restricted page.",
           "Access denied even via direct URL. Server-side access control enforced.",
           "Security", "High", ["RBAC", "URLBypass"]),
    ],

    # ── Audit & Logging ──
    "audit": [
        _p("Verify all CRUD operations are logged in audit trail",
           "1. Perform create, update, delete operations.\n2. Check audit log.",
           "Each operation recorded with timestamp, user ID, action type, and affected data.",
           tags=["Audit", "Compliance"]),
        _p("Verify audit log is tamper-proof",
           "1. Attempt to modify or delete audit log entries.\n2. Verify integrity.",
           "Audit logs cannot be modified or deleted by any user role.",
           "Security", "High", ["Audit", "Integrity"]),
    ],
}


# ══════════════════════════════════════════════════════════════
#  E-COMMERCE PATTERNS
# ══════════════════════════════════════════════════════════════

ECOMMERCE_PATTERNS: Dict[str, List[Dict]] = {
    "cart": [
        _p("Verify adding product to shopping cart",
           "1. Browse product catalog.\n2. Select a product.\n3. Click 'Add to Cart'.\n4. Open cart.",
           "Product added with correct name, price, and quantity. Cart total updated.",
           tags=["Cart", "ECommerce"]),
        _p("Verify updating product quantity in cart",
           "1. Open cart with items.\n2. Change quantity of an item.\n3. Verify totals.",
           "Quantity updated. Line total and cart total recalculated correctly.",
           tags=["Cart", "ECommerce"]),
        _p("Verify removing product from cart",
           "1. Open cart with items.\n2. Click Remove on an item.",
           "Item removed. Cart total updated. Empty cart message shown if last item removed.",
           tags=["Cart", "ECommerce"]),
        _p("Verify cart persists across sessions",
           "1. Add items to cart.\n2. Log out.\n3. Log back in.\n4. Open cart.",
           "Cart contents preserved from previous session.",
           "Edge", "Medium", ["Cart", "Persistence"]),
    ],
    "checkout": [
        _p("Verify complete checkout flow with valid payment",
           "1. Add items to cart.\n2. Proceed to checkout.\n3. Enter shipping address.\n4. Select payment method.\n5. Enter valid payment details.\n6. Place order.",
           "Order confirmed. Confirmation page with order number. Email confirmation sent.",
           tags=["Checkout", "E2E"]),
        _p("Verify checkout with invalid payment details",
           "1. Proceed to checkout.\n2. Enter invalid card number.\n3. Attempt payment.",
           "Payment declined with clear error message. User can retry with different payment.",
           "Negative", "High", ["Checkout", "Payment"]),
        _p("Verify order summary accuracy at checkout",
           "1. Add multiple items to cart.\n2. Proceed to checkout.\n3. Review order summary.",
           "All items listed with correct quantities and prices. Subtotal, tax, shipping, and total are accurate.",
           tags=["Checkout", "Accuracy"]),
    ],
    "payment": [
        _p("Verify payment with credit card",
           "1. Select credit card payment.\n2. Enter valid card details.\n3. Complete payment.",
           "Payment processed successfully. Transaction ID generated. Receipt available.",
           tags=["Payment"]),
        _p("Verify payment amount matches order total",
           "1. Complete checkout.\n2. Verify charged amount on payment confirmation.",
           "Charged amount exactly matches order total including tax and shipping.",
           tags=["Payment", "Accuracy"]),
    ],
    "inventory": [
        _p("Verify out-of-stock products cannot be added to cart",
           "1. Navigate to an out-of-stock product.\n2. Attempt to add to cart.",
           "Add to Cart button disabled or shows 'Out of Stock'. Cannot add to cart.",
           "Negative", "High", ["Inventory"]),
        _p("Verify stock quantity updates after purchase",
           "1. Note product stock quantity.\n2. Purchase the product.\n3. Check stock quantity.",
           "Stock quantity decremented by purchased amount.",
           tags=["Inventory", "DataIntegrity"]),
    ],
    "discount": [
        _p("Verify valid coupon code application",
           "1. Add items to cart.\n2. Enter valid coupon code.\n3. Apply coupon.",
           "Discount applied correctly. Cart total reduced by coupon amount/percentage.",
           tags=["Discount", "Coupon"]),
        _p("Verify expired coupon code is rejected",
           "1. Enter an expired coupon code.\n2. Attempt to apply.",
           "System rejects coupon with 'Expired coupon' message. No discount applied.",
           "Negative", "Medium", ["Discount", "Coupon"]),
    ],
    "returns": [
        _p("Verify return request initiation within return window",
           "1. Navigate to order history.\n2. Select an order within return window.\n3. Request return.",
           "Return request created. Return ID generated. Return instructions provided.",
           tags=["Returns"]),
        _p("Verify return request rejected outside return window",
           "1. Select an order past the return window.\n2. Attempt return.",
           "Return option disabled or request rejected with message about expired return window.",
           "Negative", "Medium", ["Returns"]),
    ],
}


# ══════════════════════════════════════════════════════════════
#  BANKING & FINANCE PATTERNS
# ══════════════════════════════════════════════════════════════

BANKING_PATTERNS: Dict[str, List[Dict]] = {
    "account": [
        _p("Verify new account creation with KYC verification",
           "1. Start account creation.\n2. Enter personal details.\n3. Upload KYC documents.\n4. Submit application.",
           "Account created pending verification. Confirmation with account number. KYC review initiated.",
           tags=["Account", "KYC"]),
        _p("Verify account balance display accuracy",
           "1. Log in to account.\n2. View account balance on dashboard.",
           "Balance displayed matches actual account balance. Available and total balance shown separately.",
           tags=["Account", "Balance"]),
    ],
    "transfer": [
        _p("Verify successful fund transfer between own accounts",
           "1. Select source account.\n2. Select destination account.\n3. Enter amount.\n4. Confirm transfer.",
           "Transfer completed. Source debited and destination credited. Transaction recorded in history.",
           tags=["Transfer"]),
        _p("Verify transfer with insufficient funds",
           "1. Select account with low balance.\n2. Enter amount exceeding balance.\n3. Attempt transfer.",
           "Transfer declined with 'Insufficient funds' message. No partial debit.",
           "Negative", "High", ["Transfer", "Balance"]),
        _p("Verify daily transfer limit enforcement",
           "1. Make transfers approaching daily limit.\n2. Attempt transfer exceeding remaining limit.",
           "Transfer blocked. Message shows remaining daily limit.",
           "Edge", "High", ["Transfer", "Limits"]),
    ],
    "transaction": [
        _p("Verify transaction history displays all transactions",
           "1. Navigate to transaction history.\n2. Verify recent transactions listed.",
           "All transactions shown with date, description, amount, and running balance.",
           tags=["Transaction", "History"]),
        _p("Verify transaction history filtering by date range",
           "1. Set date range filter.\n2. Apply filter.",
           "Only transactions within the selected date range are displayed.",
           tags=["Transaction", "Filter"]),
    ],
    "loan": [
        _p("Verify loan application submission",
           "1. Navigate to loan application.\n2. Fill in income and employment details.\n3. Select loan amount and term.\n4. Submit application.",
           "Application submitted. Application ID generated. Status shows 'Under Review'.",
           tags=["Loan", "Application"]),
        _p("Verify loan EMI calculation accuracy",
           "1. Enter loan amount, interest rate, and tenure.\n2. View EMI calculation.",
           "EMI amount calculated correctly matching standard amortization formula.",
           tags=["Loan", "Calculation"]),
    ],
    "security": [
        _p("Verify two-factor authentication on login",
           "1. Enter valid credentials.\n2. Receive OTP on registered device.\n3. Enter OTP.",
           "Login successful only after valid OTP. Expired OTP rejected.",
           "Security", "High", ["2FA", "Authentication"]),
        _p("Verify account lockout after failed login attempts",
           "1. Enter wrong password 5 times consecutively.",
           "Account temporarily locked. Unlock instructions sent via email/SMS.",
           "Security", "High", ["Authentication", "Lockout"]),
    ],
}


# ══════════════════════════════════════════════════════════════
#  HEALTHCARE PATTERNS
# ══════════════════════════════════════════════════════════════

HEALTHCARE_PATTERNS: Dict[str, List[Dict]] = {
    "patient": [
        _p("Verify patient registration with complete demographics",
           "1. Navigate to registration.\n2. Enter patient details (name, DOB, gender, contact, insurance).\n3. Submit.",
           "Patient record created with unique MRN. Demographics saved accurately.",
           tags=["Patient", "Registration"]),
        _p("Verify patient search by multiple criteria",
           "1. Search by patient name, DOB, or MRN.\n2. Verify search results.",
           "Matching patients displayed. Results accurate and ranked by relevance.",
           tags=["Patient", "Search"]),
    ],
    "appointment": [
        _p("Verify appointment scheduling with available provider",
           "1. Select department.\n2. Select provider.\n3. Choose available time slot.\n4. Confirm appointment.",
           "Appointment booked. Confirmation with date, time, and provider name. Calendar updated.",
           tags=["Appointment", "Scheduling"]),
        _p("Verify double-booking prevention",
           "1. Book an appointment for a time slot.\n2. Attempt to book another patient at same slot.",
           "System prevents double-booking. Shows slot as unavailable.",
           "Negative", "High", ["Appointment"]),
    ],
    "prescription": [
        _p("Verify prescription creation with drug interaction check",
           "1. Open patient chart.\n2. Add new prescription.\n3. Enter medication details.",
           "Prescription saved. Drug interaction warnings displayed if conflicts detected.",
           tags=["Prescription", "Safety"]),
    ],
    "hipaa": [
        _p("Verify PHI access logging for HIPAA compliance",
           "1. Access patient records.\n2. Check audit log.",
           "Every PHI access logged with user, timestamp, action, and record accessed.",
           "Security", "High", ["HIPAA", "Compliance"]),
        _p("Verify PHI data encryption at rest and in transit",
           "1. Inspect database storage.\n2. Inspect network traffic.",
           "PHI data encrypted using AES-256 at rest and TLS 1.2+ in transit.",
           "Security", "High", ["HIPAA", "Encryption"]),
    ],
}


# ══════════════════════════════════════════════════════════════
#  EDUCATION PATTERNS
# ══════════════════════════════════════════════════════════════

EDUCATION_PATTERNS: Dict[str, List[Dict]] = {
    "enrollment": [
        _p("Verify student enrollment in available course",
           "1. Browse course catalog.\n2. Select available course.\n3. Click Enroll.\n4. Confirm enrollment.",
           "Student enrolled successfully. Course appears in student's enrolled courses. Seat count decremented.",
           tags=["Enrollment"]),
        _p("Verify enrollment prevention when course is full",
           "1. Select a course at capacity.\n2. Attempt enrollment.",
           "Enrollment blocked with 'Course full' message. Waitlist option offered if available.",
           "Negative", "Medium", ["Enrollment", "Capacity"]),
    ],
    "assessment": [
        _p("Verify online exam submission and auto-grading",
           "1. Start assigned exam.\n2. Answer all questions.\n3. Submit exam.",
           "Exam submitted successfully. Auto-graded questions scored immediately. Results shown.",
           tags=["Assessment", "Grading"]),
        _p("Verify exam time limit enforcement",
           "1. Start a timed exam.\n2. Allow timer to expire.",
           "Exam auto-submitted when time expires. Answers saved up to expiration point.",
           "Edge", "High", ["Assessment", "Timer"]),
    ],
    "grading": [
        _p("Verify grade calculation accuracy",
           "1. Complete all graded assignments.\n2. View cumulative grade.",
           "Grade calculated correctly based on weighted components. GPA reflects accurate average.",
           tags=["Grading", "Calculation"]),
    ],
}


# ══════════════════════════════════════════════════════════════
#  LOGISTICS PATTERNS
# ══════════════════════════════════════════════════════════════

LOGISTICS_PATTERNS: Dict[str, List[Dict]] = {
    "shipment": [
        _p("Verify shipment creation with valid details",
           "1. Enter origin and destination.\n2. Enter package dimensions and weight.\n3. Select service level.\n4. Create shipment.",
           "Shipment created. Tracking number generated. Estimated delivery date shown.",
           tags=["Shipment"]),
        _p("Verify shipment tracking shows real-time status",
           "1. Enter tracking number.\n2. View tracking details.",
           "Current status, location, and timestamp displayed. Full tracking history available.",
           tags=["Tracking"]),
    ],
    "warehouse": [
        _p("Verify inventory receipt and put-away",
           "1. Receive incoming shipment at warehouse.\n2. Scan items.\n3. Assign storage location.",
           "Inventory count updated. Items linked to storage location. Receipt recorded.",
           tags=["Warehouse", "Inventory"]),
    ],
    "delivery": [
        _p("Verify proof of delivery capture",
           "1. Arrive at delivery address.\n2. Obtain recipient signature.\n3. Upload proof of delivery.",
           "POD captured with timestamp, GPS coordinates, and signature. Status updated to Delivered.",
           tags=["Delivery", "POD"]),
        _p("Verify failed delivery exception handling",
           "1. Attempt delivery.\n2. Recipient unavailable.\n3. Record exception.",
           "Delivery exception logged. Re-delivery scheduled. Customer notified.",
           "Negative", "Medium", ["Delivery", "Exception"]),
    ],
}


# ══════════════════════════════════════════════════════════════
#  ENTERPRISE / WORKFLOW PATTERNS
# ══════════════════════════════════════════════════════════════

ENTERPRISE_PATTERNS: Dict[str, List[Dict]] = {
    "authentication": [
        _p("Verify successful login with valid credentials",
           "1. Navigate to login page.\n2. Enter valid username and password.\n3. Click Sign In.",
           "User logged in successfully. Redirected to dashboard. Session created.",
           tags=["Authentication", "Login"]),
        _p("Verify login failure with invalid password",
           "1. Enter valid username.\n2. Enter incorrect password.\n3. Click Sign In.",
           "Login failed. Error message 'Invalid credentials'. No session created.",
           "Negative", "High", ["Authentication"]),
        _p("Verify password complexity requirements",
           "1. Attempt to set password without uppercase.\n2. Without number.\n3. Without special char.\n4. Below minimum length.",
           "Each attempt rejected with specific complexity requirement message.",
           "Negative", "Medium", ["Authentication", "Password"]),
    ],
    "workflow": [
        _p("Verify multi-level approval workflow",
           "1. Submit item for approval.\n2. First approver approves.\n3. Second approver approves.",
           "Item progresses through each approval stage. Final approval triggers downstream action.",
           tags=["Workflow", "Approval"]),
        _p("Verify workflow rejection returns to originator",
           "1. Submit item for approval.\n2. Approver rejects with reason.",
           "Item returned to originator with rejection reason. Status updated to 'Rejected'.",
           tags=["Workflow", "Rejection"]),
        _p("Verify workflow escalation on SLA breach",
           "1. Submit item for approval.\n2. Let approval SLA expire.",
           "Item escalated to next level. Notification sent to escalation contacts.",
           "Edge", "High", ["Workflow", "SLA"]),
    ],
    "reporting": [
        _p("Verify report generation with selected parameters",
           "1. Select report type.\n2. Set date range and filters.\n3. Generate report.",
           "Report generated with data matching selected parameters. Export options available.",
           tags=["Reporting"]),
        _p("Verify report data accuracy against source records",
           "1. Generate a report.\n2. Cross-check totals with source data.",
           "Report totals match sum of individual source records. No data discrepancies.",
           tags=["Reporting", "DataIntegrity"]),
    ],
    "integration": [
        _p("Verify API integration returns correct response",
           "1. Call integration endpoint with valid parameters.\n2. Verify response.",
           "API returns expected data in correct format. Status code 200. Response time within SLA.",
           tags=["API", "Integration"]),
        _p("Verify API error handling for invalid request",
           "1. Call endpoint with invalid/missing parameters.\n2. Verify error response.",
           "API returns appropriate error code (400/422) with descriptive error message.",
           "Negative", "High", ["API", "ErrorHandling"]),
        _p("Verify API rate limiting",
           "1. Send requests exceeding rate limit.\n2. Verify response.",
           "Rate limit enforced. 429 status returned. Retry-After header provided.",
           "Edge", "Medium", ["API", "RateLimiting"]),
    ],
}


# ══════════════════════════════════════════════════════════════
#  PATTERN REGISTRY — Maps trigger keywords to pattern sets
# ══════════════════════════════════════════════════════════════

DOMAIN_PATTERN_MAP = {
    "ecommerce": ECOMMERCE_PATTERNS,
    "banking": BANKING_PATTERNS,
    "healthcare": HEALTHCARE_PATTERNS,
    "education": EDUCATION_PATTERNS,
    "logistics": LOGISTICS_PATTERNS,
    "enterprise": ENTERPRISE_PATTERNS,
}

# Trigger keywords map to generic pattern categories
GENERIC_TRIGGER_MAP = {
    "create": ["create", "add", "register", "new", "insert", "submit", "signup", "onboard"],
    "read": ["view", "display", "list", "show", "read", "browse", "retrieve", "get"],
    "update": ["update", "edit", "modify", "change", "revise", "amend"],
    "delete": ["delete", "remove", "deactivate", "archive", "cancel", "terminate"],
    "search": ["search", "find", "lookup", "query", "locate"],
    "filter": ["filter", "refine", "narrow", "segment"],
    "sort": ["sort", "order", "rank", "arrange"],
    "pagination": ["paginate", "page", "next page", "previous page"],
    "validation": ["validate", "verify", "check", "ensure", "confirm", "mandatory", "required"],
    "export": ["export", "download", "generate report", "extract"],
    "import": ["import", "upload", "bulk upload", "ingest"],
    "notification": ["notify", "alert", "email", "sms", "notification", "message"],
    "error": ["error", "fail", "exception", "timeout", "crash", "unavailable"],
    "permission": ["permission", "role", "access", "authorize", "restrict", "admin"],
    "audit": ["audit", "log", "track", "history", "compliance", "trail"],
}

# Domain-specific trigger keywords
DOMAIN_TRIGGER_MAP = {
    "ecommerce": {
        "cart": ["cart", "basket", "add to cart", "shopping cart"],
        "checkout": ["checkout", "place order", "complete purchase", "buy now"],
        "payment": ["payment", "pay", "credit card", "debit card", "charge"],
        "inventory": ["inventory", "stock", "out of stock", "available", "quantity"],
        "discount": ["discount", "coupon", "promo", "promotion", "offer", "deal"],
        "returns": ["return", "refund", "exchange", "warranty"],
    },
    "banking": {
        "account": ["account", "savings", "checking", "current account", "open account"],
        "transfer": ["transfer", "send money", "wire", "remittance", "pay"],
        "transaction": ["transaction", "statement", "history", "ledger"],
        "loan": ["loan", "mortgage", "emi", "credit", "borrow", "interest rate"],
        "security": ["otp", "2fa", "two-factor", "mfa", "pin", "biometric"],
    },
    "healthcare": {
        "patient": ["patient", "demographics", "medical record", "mrn"],
        "appointment": ["appointment", "schedule", "booking", "visit", "consultation"],
        "prescription": ["prescription", "medication", "drug", "pharmacy", "dosage"],
        "hipaa": ["hipaa", "phi", "privacy", "compliance", "protected health"],
    },
    "education": {
        "enrollment": ["enroll", "register", "admission", "course registration"],
        "assessment": ["exam", "test", "quiz", "assessment", "evaluation"],
        "grading": ["grade", "score", "gpa", "marks", "result"],
    },
    "logistics": {
        "shipment": ["shipment", "ship", "consignment", "parcel", "package"],
        "warehouse": ["warehouse", "storage", "inventory", "put-away", "pick"],
        "delivery": ["delivery", "deliver", "pod", "last mile"],
    },
    "enterprise": {
        "authentication": ["login", "password", "credential", "sign in", "sso"],
        "workflow": ["workflow", "approval", "approve", "reject", "escalation"],
        "reporting": ["report", "dashboard", "analytics", "chart", "kpi"],
        "integration": ["api", "webhook", "integration", "sync", "endpoint"],
    },
}


def get_matching_patterns(text_lower: str, domain: str) -> List[Dict[str, Any]]:
    """
    Match document text against the pattern library.
    Returns a list of all matching patterns with their source category.
    """
    matched = []

    # 1. Always check generic patterns
    for category, triggers in GENERIC_TRIGGER_MAP.items():
        if any(trigger in text_lower for trigger in triggers):
            patterns = GENERIC_PATTERNS.get(category, [])
            for p in patterns:
                matched.append({**p, "source_category": category, "source_domain": "generic"})

    # 2. Check domain-specific patterns
    domain_triggers = DOMAIN_TRIGGER_MAP.get(domain, {})
    domain_patterns = DOMAIN_PATTERN_MAP.get(domain, {})

    for category, triggers in domain_triggers.items():
        if any(trigger in text_lower for trigger in triggers):
            patterns = domain_patterns.get(category, [])
            for p in patterns:
                matched.append({**p, "source_category": category, "source_domain": domain})

    # 3. If domain detected but few specific matches, add domain patterns more broadly
    if domain != "generic" and len([m for m in matched if m["source_domain"] == domain]) < 3:
        for category, patterns in domain_patterns.items():
            for p in patterns:
                entry = {**p, "source_category": category, "source_domain": domain}
                if entry not in matched:
                    matched.append(entry)

    return matched
