import os
from dotenv import load_dotenv
from workflow import compile_workflow 

load_dotenv()
# Get API Key
api_key = os.getenv("GEMINI_API_KEY") 

if not api_key:
    print("Error: GEMINI_API_KEY not found. Check your .env file.")
    exit()

app = compile_workflow(api_key)

initial_state = {"url": "https://example.com/recipe", "reasoning_trace": []}

print("Starting Recipe Remix workflow...")
final_state = app.invoke(initial_state)

print("\n--- Final Remixed Recipe ---")
print("\n--- Reasoning Trace ---")
