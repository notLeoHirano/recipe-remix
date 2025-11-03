from agents.recipe_agent import RecipeAgent
from data_models import WorkflowState, Substitution, OriginalRecipe
from typing import Dict, Any, List
import json

class StepAdjustmentAgent(RecipeAgent):
    """
    Adjusts recipe steps based on substitutions.
    Uses the LLM to determine whether a new prep step is required
    or the substitution can be made inline in existing steps.
    """
    def run(self, state: WorkflowState) -> Dict[str, Any]:

        recipe_data = state.remix_input_recipe
        substitutions = state.substitutions

        if not recipe_data or not substitutions:
            self.add_log(state, "StepAdjustmentAgent", "No recipe or substitutions found. Skipping.")
            return state.model_dump()

        recipe = OriginalRecipe(**recipe_data.model_dump())
        self.add_log(state, "StepAdjustmentAgent", f"Adjusting {len(substitutions)} substitutions in steps.")

        # Build prompt for LLM
        subs_text = "\n".join([f"{s.original} -> {s.suggestion}" for s in substitutions])
        steps_text = "\n".join(recipe.steps)

        prompt = f"""
        You are a recipe assistant. Given the original recipe steps below and a list of substitutions,
        modify the steps to correctly incorporate the substitutions. For each substitution:
          - If it requires preparation (like blending or mixing), add a new step at the correct point.
          - If it can replace the ingredient inline, just replace it in the existing step.
        Respond ONLY with a JSON object with keys:
        {{
          "ingredients": List of final ingredients (strings),
          "steps": List of adjusted steps (strings)
        }}

        Original Ingredients:
        {recipe.ingredients}

        Original Steps:
        {steps_text}

        Substitutions:
        {subs_text}
        """

        response = self.llm.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.candidates[0].content.parts[0].text

        # Remove ```json code fences if present
        clean_text = raw_text.strip().strip("```json").strip("```")

        try:
            adjusted = json.loads(clean_text)
            recipe.ingredients = adjusted.get("ingredients", recipe.ingredients)
            recipe.steps = adjusted.get("steps", recipe.steps)
        except Exception as e:
            self.add_log(state, "StepAdjustmentAgent", f"LLM JSON parsing error: {e}")

        # Update state
        state.remix_input_recipe = recipe
        self.add_log(state, "StepAdjustmentAgent", "Steps successfully adjusted to include substitutions.")

        return state.model_dump()