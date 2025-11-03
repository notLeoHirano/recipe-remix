from agents.recipe_agent import RecipeAgent
from data_models import WorkflowState
from typing import Dict, Any, List

class StepAdjustmentAgent(RecipeAgent):
    """
    Updates recipe steps to incorporate substitutions applied to ingredients.
    """
    def run(self, state: WorkflowState) -> Dict[str, Any]:

        recipe = state.remix_input_recipe
        subs = state.substitutions or []

        if not recipe or not subs:
            self.add_log(state, "StepAdjustmentAgent", "No substitutions or recipe found. Skipping.")
            return state.model_dump()

        self.add_log(state, "StepAdjustmentAgent", f"Adjusting {len(subs)} substitutions in steps.")

        adjusted_steps: List[str] = []
        for step in recipe.steps:
            new_step = step
            for sub in subs:
                if sub.original in new_step:
                    new_step = new_step.replace(sub.original, sub.suggestion)
            adjusted_steps.append(new_step)

        recipe.steps = adjusted_steps
        state.remix_input_recipe = recipe

        self.add_log(state, "StepAdjustmentAgent", "Steps successfully adjusted to include substitutions.")
        return state.model_dump()