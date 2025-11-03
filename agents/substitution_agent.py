from agents.recipe_agent import RecipeAgent
from data_models import Substitution, WorkflowState
from typing import Dict, Any, List
import json

class SubstitutionAgent(RecipeAgent):
    """
    Suggests replacements for flagged ingredients using the LLM.
    Applies the top recommended substitution to the recipe for remixing.
    """
    def run(self, state: WorkflowState) -> Dict[str, Any]:
        
        flags = state.dietary_flags
        if not flags:
            self.add_log(state, "SubstitutionAgent", "No flags to substitute. Skipping.")
            return state.model_dump()

        self.add_log(state, "SubstitutionAgent", f"Generating substitutions for {len(flags)} flagged ingredients.")

        substitutions: List[Substitution] = []

        # Iterate over each flagged ingredient
        for f in flags:
            f_dict = f.model_dump()  # convert Pydantic model to dict
            original = f_dict["ingredient"]
            issue = f_dict.get("issue", "Avoided ingredient")
            reasoning = f_dict.get("reasoning", "")

            # Build prompt for LLM
            prompt = f"""
            Suggest up to 3 suitable replacements for the ingredient '{original}' in a recipe.
            Explain why each option works (1-2 sentences each).
            Return the output ONLY as a JSON array of objects with keys:
            "original", "suggestion", "reasoning".
            """

            # Call the LLM
            response = self.llm.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            raw_text = response.candidates[0].content.parts[0].text
            clean_text = raw_text.strip().strip("```json").strip("```")

            try:
                suggested_list: List[Dict[str, str]] = json.loads(clean_text)
            except Exception as e:
                self.add_log(state, "SubstitutionAgent", f"LLM parsing error for {original}: {e}")
                continue

            # Validate each substitution
            validated_subs = []
            for s in suggested_list:
                try:
                    validated_subs.append(Substitution(**s))
                except Exception as e:
                    self.add_log(state, "SubstitutionAgent", f"Skipping invalid substitution {s}: {e}")

            if validated_subs:
                substitutions.extend(validated_subs)

        state.substitutions = substitutions

        # Apply top recommended substitution for remixing
        remix_recipe_data = state.remix_input_recipe
        if remix_recipe_data and substitutions:
            remix_recipe = remix_recipe_data
            for sub in substitutions:
                # Replace only the first matching ingredient with the top suggestion
                remix_recipe.ingredients = [
                    sub.suggestion if sub.original in ing else ing
                    for ing in remix_recipe.ingredients
                ]
            state.remix_input_recipe = remix_recipe
            self.add_log(state, "SubstitutionAgent", f"Applied top substitutions for {len(substitutions)} items.")

        return state.model_dump()