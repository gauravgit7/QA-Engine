import logging
import requests
from requests.auth import HTTPBasicAuth
from typing import Optional

logger = logging.getLogger("firstfintech")


def fetch_jira_story(
    base_url: str,
    email: str,
    api_token: str,
    story_id: str,
) -> dict:
    """
    Fetch a Jira issue/story by its key using the Jira REST API v3.
    Returns a simplified dict with title, description, and acceptance criteria.
    """
    if not base_url or not email or not api_token:
        logger.warning("Jira credentials are not fully configured.")
        return _mock_jira_story(story_id)

    url = f"{base_url.rstrip('/')}/rest/api/3/issue/{story_id}"
    headers = {
        "Accept": "application/json",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            auth=HTTPBasicAuth(email, api_token),
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        fields = data.get("fields", {})

        # Extract description - handle Atlassian Document Format (ADF)
        description = ""
        desc_field = fields.get("description")
        if isinstance(desc_field, str):
            description = desc_field
        elif isinstance(desc_field, dict):
            description = _extract_adf_text(desc_field)

        return {
            "key": data.get("key", story_id),
            "title": fields.get("summary", "Untitled Story"),
            "description": description,
            "status": fields.get("status", {}).get("name", "Unknown"),
            "priority": fields.get("priority", {}).get("name", "Medium"),
            "acceptance_criteria": description,  # Often embedded in description
        }

    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to Jira at {base_url}")
        return _mock_jira_story(story_id)
    except requests.exceptions.HTTPError as e:
        logger.error(f"Jira API returned error: {e.response.status_code} - {e.response.text[:200]}")
        if e.response.status_code == 401:
            raise Exception("Jira authentication failed. Check your email and API token.")
        elif e.response.status_code == 404:
            raise Exception(f"Jira story '{story_id}' not found.")
        raise Exception(f"Jira API error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Unexpected Jira error: {e}")
        return _mock_jira_story(story_id)


def _extract_adf_text(adf: dict) -> str:
    """Recursively extract text from Atlassian Document Format."""
    texts = []
    if adf.get("type") == "text":
        texts.append(adf.get("text", ""))
    for child in adf.get("content", []):
        texts.append(_extract_adf_text(child))
    return " ".join(texts).strip()


def _mock_jira_story(story_id: str) -> dict:
    """Return a realistic mock Jira story when API is unavailable."""
    return {
        "key": story_id,
        "title": f"User Authentication Flow - {story_id}",
        "description": (
            f"As a registered user, I want to be able to log in with my email and password "
            f"so that I can access my dashboard and manage my test cases.\n\n"
            f"Acceptance Criteria:\n"
            f"- User can enter email and password\n"
            f"- System validates credentials against the database\n"
            f"- On success, user receives a JWT token and is redirected to dashboard\n"
            f"- On failure, user sees an appropriate error message\n"
            f"- Password field is masked\n"
            f"- Session expires after configured timeout"
        ),
        "status": "In Progress",
        "priority": "High",
        "acceptance_criteria": (
            "- User can enter email and password\n"
            "- System validates credentials against the database\n"
            "- On success, user is redirected to dashboard\n"
            "- On failure, user sees an error message"
        ),
    }
