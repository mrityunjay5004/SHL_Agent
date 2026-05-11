import json
import requests

API_URL = "http://127.0.0.1:8000/chat"

def run_eval(trace_path):

    with open(trace_path, "r") as f:
        trace = json.load(f)

    response = requests.post(
        API_URL,
        json={
            "messages": trace["messages"]
        }
    )

    print(response.json())