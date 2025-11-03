import os
import json
from dotenv import load_dotenv
from google import genai
from workflow import compile_workflow
from data_models import WorkflowState
import itertools
import sys
import threading
import time

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment.")

# Gemini client
class LLMClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

llm_client_instance = LLMClient(api_key)

def run_remix_workflow(state: WorkflowState):
    """Compile and execute the recipe workflow (without remixing)."""
    app = compile_workflow(llm_client_instance)
    final_state_dict = app.invoke(state.model_dump())
    final_state = WorkflowState(**final_state_dict)

    print("\nWorkflow Complete:")

    # Print full recipe with substitutions
    final_recipe = final_state.remix_input_recipe
    if final_recipe:
        print("\n## Final Recipe Ingredients:")
        for ing in final_recipe.ingredients:
            print(f"- {ing}")

        print("\n## Recipe Steps:")
        for i, step in enumerate(final_recipe.steps, 1):
            print(f"{i}. {step}")
    else:
        print("No recipe output produced.")

    # Substitution summary
    if final_state.substitutions:
        print("\n## Substitution Summary")
        
        # Group substitutions by original ingredient
        subs_by_original = {}
        for sub in final_state.substitutions:
            original = sub.original
            subs_by_original.setdefault(original, []).append(sub)

        for original, sub_list in subs_by_original.items():
            print(f"\nOriginal Ingredient: {original}")
            if sub_list:
                # Print the top recommendation first
                top = sub_list[0]
                print(f"  → Top Recommendation: {top.suggestion}")
                print(f"    Reasoning: {top.reasoning}")

                if len(sub_list) > 1:
                    print("  → Other Possible Substitutions:")
                    for alt in sub_list[1:]:
                        print(f"    - {alt.suggestion}: {alt.reasoning}")
    else:
        print("\nNo substitutions were made.")

    # Reasoning trace
    print("\n## Reasoning Trace Log")
    print(json.dumps(final_state.reasoning_trace, indent=2))

def spinner_task(stop_event):
    spinner = itertools.cycle(["|", "/", "--", "\\"])
    while not stop_event.is_set():
        sys.stdout.write(next(spinner))  # write next spinner character
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write("\b")  # backspace to overwrite

if __name__ == "__main__":
    print("=== Recipe Remix ===")
    recipe_url = input("Enter the recipe URL: ").strip()
    avoid = input("Enter ingredients to avoid (comma-separated): ").strip()
    filters = [a.strip().lower() for a in avoid.split(",") if a.strip()]

    initial_state = WorkflowState(
        url=recipe_url,
        dietary_filters=filters
    )

    # Start spinner 
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=spinner_task, args=(stop_spinner,))
    spinner_thread.start()

    try:
        run_remix_workflow(initial_state)
    finally:
        stop_spinner.set()
        spinner_thread.join()


    # Print full substituted recipe
    final_recipe = initial_state.remix_input_recipe
    if final_recipe:
        print("\n## Final Recipe Ingredients:")
        for ing in final_recipe.ingredients:
            print(f"- {ing}")

        print("\n## Recipe Steps:")
        for i, step in enumerate(final_recipe.steps, 1):
            print(f"{i}. {step}")