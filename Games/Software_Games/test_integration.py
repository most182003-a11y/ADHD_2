import sys
import os
import requests

# Add current dir to path
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

from backend_api import create_session, save_mirror_me_trials, save_green_light_trials, save_summary, API_BASE_URL, DEVICE_KEY

HEADERS = {
    "Content-Type": "application/json",
    "X-Game-Device-Key": DEVICE_KEY
}

def get_or_create_child():
    print("Checking for existing test child...")
    url = f"{API_BASE_URL}/api/children"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            res = r.json()
            # The structure is Response<IEnumerable<Child>>
            children = res.get("data", [])
            for c in children:
                if c.get("name") == "Integration Test Child":
                    print(f"[SUCCESS] Found existing test child: {c.get('id')}")
                    return c.get("id")
    except Exception as e:
        print(f"[ERROR] Failed to list children: {e}")

    print("Test child not found. Creating a new test child...")
    child_payload = {
        "name": "Integration Test Child",
        "age": 8,
        "gender": 0,  # Male
        "diagnosisSeverity": 1,  # Moderate
        "status": 1,  # Stable
        "avatarInitials": "ITC"
    }
    try:
        r = requests.post(url, json=child_payload, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            print(f"[FAIL] Create child failed: {r.status_code} - {r.text}")
            return None
        print("[SUCCESS] Sent creation request for test child.")
    except Exception as e:
        print(f"[ERROR] Request failed during child creation: {e}")
        return None

    # Retrieve the child list again to get the ID
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            children = r.json().get("data", [])
            for c in children:
                if c.get("name") == "Integration Test Child":
                    print(f"[SUCCESS] Retrieved new test child ID: {c.get('id')}")
                    return c.get("id")
    except Exception as e:
        print(f"[ERROR] Failed to retrieve child ID: {e}")

    return None

def test_mirror_me(child_id):
    print("\nTesting Mirror Me API flow...")
    session_id = create_session(child_id, "mirror_me")
    if not session_id:
        print("[FAIL] Mirror Me: Failed to create session!")
        return False
    print(f"[SUCCESS] Created session: {session_id}")

    trials = [
        {
            "trialIndex": 1,
            "targetPoseId": "pose-1",
            "reactionTimeMs": 1200,
            "poseSimilarity": 0.85,
            "holdingDurationMs": 2000,
            "fidgetScore": 0.15,
            "prematureMovement": False,
            "attentionPercent": 0.95
        },
        {
            "trialIndex": 2,
            "targetPoseId": "pose-2",
            "reactionTimeMs": 950,
            "poseSimilarity": 0.92,
            "holdingDurationMs": 2000,
            "fidgetScore": 0.08,
            "prematureMovement": False,
            "attentionPercent": 1.0
        }
    ]

    res_trials = save_mirror_me_trials(session_id, trials)
    if not res_trials or not res_trials.get("succeeded"):
        print("[FAIL] Mirror Me: Failed to save trials!")
        return False
    print("[SUCCESS] Successfully saved trials.")

    summary = {
        "totalTrials": 2,
        "averageReactionTimeMs": 1075,
        "averageSimilarity": 0.89,
        "totalFidgetScore": 0.23,
        "attentionOverall": 0.98
    }

    res_summary = save_summary(session_id, summary)
    if not res_summary or not res_summary.get("succeeded"):
        print("[FAIL] Mirror Me: Failed to save summary!")
        return False
    print("[SUCCESS] Successfully saved summary.")
    print("[PASS] Mirror Me Flow Test Passed!")
    return True

def test_green_light(child_id):
    print("\nTesting Green Light API flow...")
    session_id = create_session(child_id, "green_light")
    if not session_id:
        print("[FAIL] Green Light: Failed to create session!")
        return False
    print(f"[SUCCESS] Created session: {session_id}")

    trials = [
        {
            "trialIndex": 1,
            "phase": "GreenLight",
            "stopSignalDelayMs": 0,
            "movementIntensity": 0.12,
            "stopReactionTimeMs": 450,
            "freezeQuality": None,
            "falseStart": None
        },
        {
            "trialIndex": 2,
            "phase": "RedLight",
            "stopSignalDelayMs": 800,
            "movementIntensity": None,
            "stopReactionTimeMs": None,
            "freezeQuality": 1.0,
            "falseStart": False
        }
    ]

    res_trials = save_green_light_trials(session_id, trials)
    if not res_trials or not res_trials.get("succeeded"):
        print("[FAIL] Green Light: Failed to save trials!")
        return False
    print("[SUCCESS] Successfully saved trials.")

    summary = {
        "totalTrials": 2,
        "averageStopReactionTimeMs": 450,
        "falseStartCount": 0,
        "averageFreezeQuality": 1.0,
        "movementIntensityOverall": 0.12
    }

    res_summary = save_summary(session_id, summary)
    if not res_summary or not res_summary.get("succeeded"):
        print("[FAIL] Green Light: Failed to save summary!")
        return False
    print("[SUCCESS] Successfully saved summary.")
    print("[PASS] Green Light Flow Test Passed!")
    return True


def test_simon_memory(child_id):
    print("\nTesting Simon Memory API flow...")
    session_id = create_session(child_id, "SimonMemory")
    if not session_id:
        print("[FAIL] Simon Memory: Failed to create session!")
        return False
    print(f"[SUCCESS] Created session: {session_id}")

    trials = [
        {
            "level": 1,
            "sequenceLength": 3,
            "speed": 0.56,
            "step": 1,
            "expected": 3,
            "pressed": 4,
            "correct": False,
            "reactionTimeMs": 5749.0
        }
    ]

    res_trials = save_simon_trials(session_id, trials)
    if not res_trials or not res_trials.get("succeeded"):
        print("[FAIL] Simon Memory: Failed to save trials!")
        return False
    print("[SUCCESS] Successfully saved trials.")

    summary = {
        "totalTrials": 1,
        "finalLevel": 1,
        "totalCorrectSteps": 0,
        "totalSteps": 1,
        "prematurePressesDuringShow": 0,
        "endStatus": "lost"
    }

    res_summary = save_summary(session_id, summary)
    if not res_summary or not res_summary.get("succeeded"):
        print("[FAIL] Simon Memory: Failed to save summary!")
        return False
    print("[SUCCESS] Successfully saved summary.")
    print("[PASS] Simon Memory Flow Test Passed!")
    return True


def test_reaction_time(child_id):
    print("\nTesting Reaction Time API flow...")
    session_id = create_session(child_id, "ReactionTime")
    if not session_id:
        print("[FAIL] Reaction Time: Failed to create session!")
        return False
    print(f"[SUCCESS] Created session: {session_id}")

    trials = [
        {
            "trial": 1,
            "targetLED": 2,
            "delay": 2.346,
            "result": "hit",
            "pressedButton": 2,
            "reactionTimeMs": 623.4,
            "correct": True,
            "impulsiveError": False
        },
        {
            "trial": 2,
            "targetLED": 5,
            "delay": 3.871,
            "result": "false_start",
            "pressedButton": 5,
            "reactionTimeMs": None,
            "correct": False,
            "impulsiveError": True
        }
    ]

    res_trials = save_reaction_trials(session_id, trials)
    if not res_trials or not res_trials.get("succeeded"):
        print("[FAIL] Reaction Time: Failed to save trials!")
        return False
    print("[SUCCESS] Successfully saved trials.")

    summary = {
        "totalTrials": 15,
        "hits": 11,
        "falseStarts": 2,
        "misses": 1,
        "impulsiveErrors": 1,
        "wrongButtons": 0,
        "averageReactionTimeMs": 587.6,
        "reactionTimeStdDevMs": 95.3,
        "impulsivityScore": 20.0,
        "attentionScore": 73.3
    }

    res_summary = save_summary(session_id, summary)
    if not res_summary or not res_summary.get("succeeded"):
        print("[FAIL] Reaction Time: Failed to save summary!")
        return False
    print("[SUCCESS] Successfully saved summary.")
    print("[PASS] Reaction Time Flow Test Passed!")
    return True


if __name__ == "__main__":
    # Import the newly added helper functions
    from backend_api import save_simon_trials, save_reaction_trials

    child_id = get_or_create_child()
    if not child_id:
        print("[FAIL] Could not find or create test child. Exiting.")
        sys.exit(1)

    success = (
        test_mirror_me(child_id)
        and test_green_light(child_id)
        and test_simon_memory(child_id)
        and test_reaction_time(child_id)
    )
    if success:
        print("\nAll integration tests passed successfully!")
        sys.exit(0)
    else:
        print("\nSome integration tests failed!")
        sys.exit(1)
