import json
import sys

try:
    with open(r"C:\Users\hema sundar\.gemini\antigravity\brain\929c071d-5ef1-452b-9a4d-92323909dabf\.system_generated\logs\transcript.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            if data.get("type") == "USER_INPUT":
                content = data.get("content", "")
                if "github.com" in content.lower():
                    print("FOUND URL:", content.strip())
except Exception as e:
    print(e)
