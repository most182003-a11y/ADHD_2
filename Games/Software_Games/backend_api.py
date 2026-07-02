import requests
import json
import time
import os

API_BASE_URL = os.getenv("ADHD_API_BASE_URL", "http://localhost:5131")
DEVICE_KEY = os.getenv("GAME_DEVICE_API_KEY", "dev-game-device-key-change-me")

# Simple log file next to the script
_LOG_DIR = os.path.dirname(os.path.abspath(__file__))
_LOG_FILE = os.path.join(_LOG_DIR, "api_sync.log")


def _log(msg):
    """Append a timestamped message to the log file and print to console."""
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    try:
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _post(endpoint, data, retries=3, backoff=1.5):
    """POST with automatic retry and exponential backoff."""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "X-Game-Device-Key": DEVICE_KEY,
    }
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(url, json=data, headers=headers, timeout=10)
            resp.raise_for_status()
            _log(f"OK {endpoint} (attempt {attempt}) -> {resp.status_code}")
            return resp.json()
        except requests.RequestException as e:
            last_error = e
            detail = ""
            if hasattr(e, 'response') and e.response is not None:
                detail = f" | Response: {e.response.text[:300]}"
            _log(f"FAIL {endpoint} (attempt {attempt}/{retries}): {e}{detail}")
            if attempt < retries:
                time.sleep(backoff * attempt)

    _log(f"GAVE UP {endpoint} after {retries} attempts: {last_error}")
    return None


def create_session(child_id, game_type):
    """Create a new game session on the backend. Returns session ID or None."""
    data = {"childId": child_id, "gameType": game_type}
    result = _post("/api/sessions", data)
    if result and result.get("succeeded"):
        session_id = result["data"]["id"]
        _log(f"Session created: {session_id} (child={child_id}, game={game_type})")
        return session_id
    return None


def save_mirror_me_trials(session_id, trials):
    """Save Mirror Me trial results to an existing session."""
    result = _post(f"/api/sessions/{session_id}/mirror-me-trials", {"trials": trials})
    if result and result.get("succeeded"):
        _log(f"{len(trials)} Mirror Me trials saved to session {session_id}")
    return result


def save_green_light_trials(session_id, trials):
    """Save Green Light trial results to an existing session."""
    result = _post(f"/api/sessions/{session_id}/green-light-trials", {"trials": trials})
    if result and result.get("succeeded"):
        _log(f"{len(trials)} Green Light trials saved to session {session_id}")
    return result


def save_summary(session_id, summary):
    """Save session summary (works for both game types)."""
    result = _post(f"/api/sessions/{session_id}/summary", summary)
    if result and result.get("succeeded"):
        _log(f"Summary saved for session {session_id}")
    return result
