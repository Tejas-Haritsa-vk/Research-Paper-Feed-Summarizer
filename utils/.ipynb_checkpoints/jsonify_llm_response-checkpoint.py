import json
import re

def jsonify_llm_response(llm_response):
    # 1️⃣ Remove the ```json ... ``` wrapper
    cleaned = re.sub(r"^```json\s*|\s*```$", "", llm_response.strip())
    
    # 2️⃣ Parse to Python dict
    parsed = json.loads(cleaned)
    
    return parsed