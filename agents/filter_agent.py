from agents.recipe_agent import RecipeAgent
from data_models import OriginalRecipe, Flag, WorkflowState
from typing import Dict, Any, List
import json

class DietaryFilterAgent(RecipeAgent):
    """
    Checks ingredients based solely on user-specified avoided ingredients.
    Uses the LLM to generate structured dietary flags.
    """
    def run(self, state: WorkflowState) -> Dict[str, Any]:

        recipe_data = state.original_recipe
        if not recipe_data:
            self.add_log(state, "DietaryFilterAgent", "Skipped: No valid recipe found.")
            return state.model_dump()

        recipe = OriginalRecipe(**recipe_data.model_dump())
        self.add_log(state, "DietaryFilterAgent", "Starting dietary analysis based on user preferences.")

        avoided = state.dietary_filters or []
        if not avoided:
            self.add_log(state, "DietaryFilterAgent", "No user-specified ingredients to avoid.")
            return state.model_dump()

        # Prompt the LLM to detect only the user-specified ingredients
        prompt = f"""
        Analyze the following ingredient list for the user-specified avoided ingredients: {avoided}.
        
        Ingredients: {recipe.ingredients}

        Respond ONLY with a JSON array where each item matches the Pydantic model 'Flag':
        {{
            "ingredient": str,
            "issue": str,
            "reasoning": str
        }}
        """

        raw_flags: List[Dict[str, str]] = []

        # Call LLM
        response = self.llm.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.candidates[0].content.parts[0].text

        # Remove ```json and ``` if present
        clean_text = raw_text.strip().strip("```json").strip("```")

        try:
            raw_flags = json.loads(clean_text)
        except json.JSONDecodeError as e:
            self.add_log(state, "DietaryFilterAgent", f"JSON parsing error: {e}")
            raw_flags = []

        # Validate each flag with Pydantic
        validated_flags: List[Flag] = []
        for f in raw_flags:
            try:
                validated_flags.append(Flag(**f))
            except Exception as e:
                self.add_log(state, "DietaryFilterAgent", f"Skipping invalid flag {f}: {e}")

        # Store as Flag objects for type safety
        state.dietary_flags = validated_flags
        state.remix_input_recipe = recipe

        self.add_log(state, "DietaryFilterAgent", f"Detected {len(validated_flags)} dietary issues.")
        return state.model_dump()