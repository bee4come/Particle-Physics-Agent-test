import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def create_session():
    """Creates a new session and returns the session ID."""
    url = f"{BASE_URL}/apps/feynmancraft_adk/users/user/sessions"
    headers = {"Content-Type": "application/json"}
    data = {"state": {}, "events": []}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        session = response.json()
        session_id = session.get("id")
        if not session_id:
            print("Error: Could not get session ID from response.")
            sys.exit(1)
        print(f"Successfully created session: {session_id}")
        return session_id
    except requests.exceptions.RequestException as e:
        print(f"Error creating session: {e}")
        sys.exit(1)

def run_agent(session_id, user_request):
    """Runs the agent with the given session ID and user request."""
    url = f"{BASE_URL}/run"
    headers = {"Content-Type": "application/json"}
    data = {
        "appName": "feynmancraft_adk",
        "userId": "user",
        "sessionId": session_id,
        "newMessage": {
            "parts": [{"text": user_request}],
            "role": "user"
        },
        "streaming": False
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print("Agent run successful. Response:")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error running agent: {e}")
        if e.response:
            try:
                print("Error response:", e.response.json())
            except json.JSONDecodeError:
                print("Error response:", e.response.text)
        sys.exit(1)

if __name__ == "__main__":
    request = "positron and electron"
    print(f"Testing with request: '{request}'")
    session_id = create_session()
    run_agent(session_id, request)
    print("\nTest completed successfully!")
