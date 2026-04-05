"""Quick API test for the UAT generation engine."""
import requests
import json

BASE = "http://localhost:8000"

# 1. Login
r = requests.post(f"{BASE}/auth/login", json={
    "email": "admin@firstfintech.com",
    "password": "admin123"
})
token = r.json()["token"]
print("Login OK")

# 2. Generate UAT test cases
headers = {"Authorization": f"Bearer {token}"}
formdata = {
    "manual_text": (
        "As an admin, I want to manage user accounts including creating new users, "
        "updating user roles, resetting passwords, and deactivating accounts. "
        "The system shall validate email format and enforce password complexity. "
        "Users must be able to search and filter the user list. "
        "The system should send email notifications when accounts are created or passwords are reset. "
        "User roles include Admin, Manager, and Viewer. "
        "The admin dashboard shall display user statistics and activity logs. "
        "The system must support export of user data to Excel and CSV. "
        "When a user's account is deactivated, the system must revoke all active sessions. "
        "The system shall log all account changes in an audit trail. "
        "Managers can approve new user registrations but cannot delete accounts."
    ),
    "generation_method": "rules",
    "target_count": "50",
    "test_case_id": "TC-UAT",
}

r2 = requests.post(f"{BASE}/generate/uat", data=formdata, headers=headers)
resp = r2.json()

print(f"\nSuccess: {resp['success']}")
print(f"Total Generated: {resp['total_generated']}")
print(f"Domain Detected: {resp['domain_detected']}")
print(f"Requirements Found: {resp['total_requirements_found']}")
print(f"Coverage: {resp['coverage_percentage']}%")
print(f"Method Used: {resp['method_used']}")
print(f"Generation Time: {resp['generation_time']:.3f}s")

print(f"\n--- First 10 Test Cases ---")
for tc in resp["testCases"][:10]:
    print(f"  {tc['id']}  [{tc['test_type']:10s}]  {tc['priority']:6s}  {tc['title'][:80]}")

print(f"\n--- Coverage Report ---")
cov = resp.get("coverage_report", {})
print(f"  Requirement Coverage: {cov.get('requirement_coverage', {}).get('coverage_percentage', 0)}%")
print(f"  Role Coverage: {cov.get('role_coverage', {}).get('coverage_percentage', 0)}%")
print(f"  Module Coverage: {cov.get('module_coverage', {}).get('coverage_percentage', 0)}%")
print(f"  Test Type Distribution: {cov.get('test_type_distribution', {})}")
