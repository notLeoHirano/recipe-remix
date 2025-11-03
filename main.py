import os
import json
from dotenv import load_dotenv
from google import genai
from workflow import compile_workflow
from data_models import WorkflowState

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
    """Compile and execute the recipe remix workflow."""
    app = compile_workflow(llm_client_instance)
    final_state_dict = app.invoke(state.model_dump())
    final_state = WorkflowState(**final_state_dict)

    print("\nWorkflow Complete:")
    print("\n## Final Remixed Recipe")
    if final_state.remixed_recipe:
        print(json.dumps(final_state.remixed_recipe, indent=4))
    else:
        print("No remix output produced.")

    print("\n## Substitution Summary")
    if final_state.substitutions:
        print(json.dumps([s.model_dump() for s in final_state.substitutions], indent=4))
    else:
        print("No substitutions were made.")

    print("\n## Reasoning Trace Log")
    print(json.dumps(final_state.reasoning_trace, indent=2))

if __name__ == "__main__":
    print("=== Recipe Adjustment ===")
    recipe_url = input("Enter the recipe URL: ").strip()
    avoid = input("Enter ingredients to avoid (comma-separated): ").strip()
    filters = [a.strip().lower() for a in avoid.split(",") if a.strip()]

    initial_state = WorkflowState(
        url=recipe_url,
        dietary_filters=filters
    )

    run_remix_workflow(initial_state)

    # Print full substituted recipe
    final_recipe = initial_state.remix_input_recipe
    if final_recipe:
        print("\n## Final Recipe Ingredients:")
        for ing in final_recipe.ingredients:
            print(f"- {ing}")

        print("\n## Recipe Steps:")
        for i, step in enumerate(final_recipe.steps, 1):
            print(f"{i}. {step}")