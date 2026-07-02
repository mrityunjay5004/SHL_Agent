import google.generativeai as genai
import os



from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-3.5-flash")

import time
import google.api_core.exceptions

def generate_llm_response(prompt):
    max_retries = 6
    backoff = 3.0
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except google.api_core.exceptions.ResourceExhausted as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(backoff)
            backoff *= 2.0
        except Exception as e:
            # Handle string-based rate limit errors
            err_msg = str(e).lower()
            if "quota" in err_msg or "limit" in err_msg or "429" in err_msg or "resource_exhausted" in err_msg:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(backoff)
                backoff *= 2.0
            else:
                raise e