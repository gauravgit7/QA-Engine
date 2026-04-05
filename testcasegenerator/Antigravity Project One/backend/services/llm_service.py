import json
import logging
import time
from typing import List, Optional, Tuple, Dict, Any

from config.settings import settings
from services.rule_engine import generate_cases_from_story
from tenacity import retry, wait_exponential, stop_after_attempt

logger = logging.getLogger("firstfintech")

SYSTEM_PROMPT = """You are a senior QA engineer. Generate structured test cases from the provided context.
Return ONLY a valid JSON array. Each item must have these exact keys:
- id: string (e.g. "TC-001")
- title: string
- preconditions: string
- steps: string (numbered steps separated by newlines)
- expectedResult: string
- priority: string ("High", "Medium", or "Low")
- test_type: string (e.g., "Positive", "Negative", "Edge", "Security")
- test_data: string (intelligent mock data specific to the test)
- postconditions: string
- tags: array of strings
- estimated_duration: integer (seconds)

Do not include any markdown, explanation, or wrapping. Output raw JSON only."""


def build_user_prompt(
    context_text: str,
    module_type: str = "UAT",
    epic_id: Optional[str] = None,
    story_id: Optional[str] = None,
    base_test_id: Optional[str] = None,
) -> str:
    """Build the user-facing prompt to send to the LLM."""
    parts = [f"Generate {module_type} test cases for the following context:\n\n{context_text}"]
    if epic_id:
        parts.append(f"\nEpic ID: {epic_id}")
    if story_id:
        parts.append(f"\nStory ID: {story_id}")
    if base_test_id:
        parts.append(f"\nUse base test case ID prefix: {base_test_id}")
    parts.append("\nGenerate comprehensive test cases covering positive, negative, and edge scenarios based on testing best practices like equivalence partitioning and boundary value analysis.")
    return "\n".join(parts)


def estimate_tokens_and_cost(prompt: str, response: str, model: str) -> Tuple[int, float]:
    char_count = len(prompt) + len(response)
    tokens = char_count // 4  # rough heuristic
    cost = (tokens / 1000) * 0.0015  # average $0.0015 per 1k tokens
    return tokens, cost


async def generate_test_cases(
    context_text: str,
    module_type: str = "UAT",
    epic_id: Optional[str] = None,
    story_id: Optional[str] = None,
    base_test_id: Optional[str] = None,
    api_key: Optional[str] = None,
    generation_method: str = "llm",
    options: Optional[dict] = None,
    ollama_model: Optional[str] = None
) -> Tuple[List[dict], Dict[str, Any]]:
    """
    Generate test cases by calling the required method.
    Returns (test_cases, metadata)
    """
    start_time = time.time()
    options = options or {}
    
    # 1. Direct Rules Method Request
    if generation_method == "rules":
        logger.info("Using Advanced Rule Engine as requested.")
        cases = generate_cases_from_story(context_text, base_id=base_test_id, options=options)
        metadata = {
            "method_used": "rules",
            "fallback_triggered": False,
            "fallback_reason": None,
            "generation_time": time.time() - start_time,
            "token_usage": 0,
            "cost": 0.0
        }
        return cases, metadata

    # Key selection logic for LLM
    db_key = api_key if (api_key and "•" not in api_key and api_key.strip() != "") else None
    final_key = db_key or settings.OPENAI_API_KEY

    is_ollama = final_key and final_key.lower().strip() == "ollama"

    # If NO key is found or it's a placeholder (and not ollama), trigger SMART FALLBACK
    if not is_ollama and (not final_key or final_key.startswith("sk-your") or final_key.strip() == ""):
        logger.warning("No valid API key configured. Triggering Smart Fallback Engine.")
        cases = generate_cases_from_story(context_text, base_id=base_test_id, options=options)
        metadata = {
            "method_used": "rules",
            "fallback_triggered": True,
            "fallback_reason": "No API Key configured",
            "generation_time": time.time() - start_time,
            "token_usage": 0,
            "cost": 0.0
        }
        return cases, metadata

    try:
        if is_ollama:
            logger.info("Detected 'ollama' key, using local Ollama model (llama3).")
            cases, tokens, cost = await _call_ollama(context_text, module_type, epic_id, story_id, base_test_id, ollama_model or settings.OLLAMA_MODEL)
            provider = "llm_ollama"
        elif final_key.startswith("AIza"):
            logger.info("Detected Google AI Studio key, using Gemini LLM model (gemini-2.0-flash).")
            cases, tokens, cost = await _call_gemini(context_text, module_type, epic_id, story_id, base_test_id, final_key)
            provider = "llm_gemini"
        elif final_key.startswith("gsk_"):
            logger.info("Detected Groq key, using Groq model (llama-3.1-70b-versatile).")
            cases, tokens, cost = await _call_groq(context_text, module_type, epic_id, story_id, base_test_id, final_key)
            provider = "llm_groq"
        else:
            logger.info("Detected OpenAI key, using OpenAI GPT model (gpt-4o-mini).")
            cases, tokens, cost = await _call_openai(context_text, module_type, epic_id, story_id, base_test_id, final_key)
            provider = "llm_openai"
            
        metadata = {
            "method_used": provider,
            "fallback_triggered": False,
            "fallback_reason": None,
            "generation_time": time.time() - start_time,
            "token_usage": tokens,
            "cost": cost
        }
        return cases, metadata

    except Exception as e:
        logger.error(f"LLM API call failed with error: {str(e)}. Triggering Smart Fallback Engine as safety measure.")
        cases = generate_cases_from_story(context_text, base_id=base_test_id, options=options)
        metadata = {
            "method_used": "rules",
            "fallback_triggered": True,
            "fallback_reason": f"API Error: {str(e)}",
            "generation_time": time.time() - start_time,
            "token_usage": 0,
            "cost": 0.0
        }
        return cases, metadata


@retry(stop=stop_after_attempt(int(settings.LLM_RETRY_COUNT)), wait=wait_exponential(multiplier=1, min=2, max=10))
async def _call_gemini(context_text, module_type, epic_id, story_id, base_test_id, api_key) -> Tuple[List[dict], int, float]:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    user_prompt = build_user_prompt(context_text, module_type, epic_id, story_id, base_test_id)
    full_prompt = f"{SYSTEM_PROMPT}\n\nTask:\n{user_prompt}"

    response = model.generate_content(full_prompt)
    content = response.text.strip()
    return _parse_json_response(content, full_prompt, "gemini-2.0-flash")


@retry(stop=stop_after_attempt(int(settings.LLM_RETRY_COUNT)), wait=wait_exponential(multiplier=1, min=2, max=10))
async def _call_openai(context_text, module_type, epic_id, story_id, base_test_id, api_key) -> Tuple[List[dict], int, float]:
    from openai import OpenAI
    import httpx
    http_client = httpx.Client(trust_env=False)
    client = OpenAI(api_key=api_key, http_client=http_client, timeout=settings.LLM_TIMEOUT_SECONDS)

    user_prompt = build_user_prompt(context_text, module_type, epic_id, story_id, base_test_id)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        temperature=0.7,
        max_tokens=2000,
    )
    content = response.choices[0].message.content.strip()
    return _parse_json_response(content, SYSTEM_PROMPT + user_prompt, "gpt-3.5-turbo")


@retry(stop=stop_after_attempt(int(settings.LLM_RETRY_COUNT)), wait=wait_exponential(multiplier=1, min=2, max=10))
async def _call_groq(context_text, module_type, epic_id, story_id, base_test_id, api_key) -> Tuple[List[dict], int, float]:
    from groq import Groq
    import httpx
    http_client = httpx.Client(trust_env=False)
    client = Groq(api_key=api_key, http_client=http_client, timeout=settings.LLM_TIMEOUT_SECONDS)

    user_prompt = build_user_prompt(context_text, module_type, epic_id, story_id, base_test_id)

    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        temperature=0.7,
        max_tokens=2000,
    )
    content = response.choices[0].message.content.strip()
    return _parse_json_response(content, SYSTEM_PROMPT + user_prompt, "llama-3.1-70b-versatile")


@retry(stop=stop_after_attempt(int(settings.LLM_RETRY_COUNT)), wait=wait_exponential(multiplier=1, min=2, max=10))
async def _call_ollama(context_text, module_type, epic_id, story_id, base_test_id, ollama_model: str) -> Tuple[List[dict], int, float]:
    import requests
    
    url = "http://127.0.0.1:11434/api/chat"
    user_prompt = build_user_prompt(context_text, module_type, epic_id, story_id, base_test_id)
    
    payload = {
        "model": ollama_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 2048
        }
    }
    
    # Using synchronous requests with long timeout - more stable for local IPC on Windows
    timeout = 300.0
    
    logger.info(f"Sending request to Ollama @ {url} for model '{payload['model']}'...")
    
    try:
        # Explicitly disable proxies for local connection
        session = requests.Session()
        session.trust_env = False 
        
        response = session.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        logger.info("Ollama responded successfully.")
    except requests.exceptions.Timeout:
        logger.error("Ollama request timed out after 300s.")
        raise
    except Exception as e:
        logger.error(f"Ollama request error: {str(e)}")
        raise
        
    content = data.get("message", {}).get("content", "").strip()
    
    # Cost is effectively 0 for local Ollama, we estimate tokens
    tokens, _ = estimate_tokens_and_cost(SYSTEM_PROMPT + user_prompt, content, "dolphin-llama3:latest")
    # Call _parse_json_response directly to return tuples of (test_cases, int, float)
    return _parse_json_response(content, SYSTEM_PROMPT + user_prompt, "dolphin-llama3:latest")


async def is_ollama_running() -> bool:
    """Check if Ollama server is reachable and responsive."""
    import requests
    # Try 127.0.0.1 first, then fallback to localhost
    for host in ["127.0.0.1", "localhost"]:
        try:
            url = f"http://{host}:11434/api/tags"
            response = requests.get(url, timeout=3.0)
            if response.status_code == 200:
                logger.info(f"Ollama API confirmed online via {host}.")
                return True
        except Exception:
            continue
            
    logger.debug("Ollama health check failed on all local addresses.")
    return False


async def warmup_ollama() -> bool:
    """Trigger a lightweight prompt to load dolphin-llama3 into RAM."""
    import requests
    if not await is_ollama_running():
        return False
        
    logger.info("Warming up Ollama (dolphin-llama3:latest)...")
    payload = {
        "model": "dolphin-llama3:latest",
        "messages": [{"role": "user", "content": "hi"}],
        "stream": False
    }
    try:
        # 30s timeout for initial load
        requests.post("http://127.0.0.1:11434/api/chat", json=payload, timeout=30.0)
        logger.info("Ollama is warmed up and ready.")
        return True
    except Exception as e:
        logger.error(f"Ollama warmup failed: {str(e)}")
        return False


def _parse_json_response(content: str, full_prompt: str, model_name: str) -> Tuple[List[dict], int, float]:
    original_content = content
    if content.startswith("```"):
        lines = content.split("\\n")
        content = "\\n".join(lines[1:])
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        if content.startswith("json\\n"):
            content = content[5:]

    test_cases = json.loads(content)
    if not isinstance(test_cases, list):
        raise ValueError("LLM response is not a JSON array")

    tokens, cost = estimate_tokens_and_cost(full_prompt, original_content, model_name)
    return test_cases, tokens, cost
