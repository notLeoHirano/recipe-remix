import unittest
from unittest.mock import MagicMock
from data_models import WorkflowState, Flag, OriginalRecipe
from agents.substitution_agent import SubstitutionAgent
from agents.filter_agent import DietaryFilterAgent

class TestRecipeWorkflow(unittest.TestCase):
    def setUp(self):
        # Minimal recipe state used in all tests
        recipe_data = OriginalRecipe(
            title="Pancakes",
            ingredients=["1 egg", "3 tablespoons butter", "flour", "milk"],
            steps=["Mix ingredients", "Cook pancakes"]
        )

        self.state = WorkflowState(
            url="https://www.allrecipes.com/recipe/21014/good-old-fashioned-pancakes/",
            dietary_filters=["egg"],       
            original_recipe=recipe_data,  
            remix_input_recipe=recipe_data  
        )

    def test_nonvegan_restriction_flags(self):
        """Test that a 'nonvegan' restriction flags multiple ingredients correctly."""
        mock_llm = MagicMock()
        mock_llm.client.models.generate_content.return_value.candidates = [
            MagicMock(content=MagicMock(parts=[MagicMock(text='''[
                {"ingredient": "1 egg", "issue": "Non-vegan", "reasoning": "Egg is animal-derived."},
                {"ingredient": "3 tablespoons butter", "issue": "Non-vegan", "reasoning": "Butter is dairy-based."}
            ]''')] ))
        ]

        agent = DietaryFilterAgent(mock_llm)
        self.state.dietary_filters = ["nonvegan"]
        result = agent.run(self.state)

        # Print flagged ingredients
        print("\n[Non-Vegan Test] Flagged Ingredients:")
        for f in self.state.dietary_flags:
            print(f"- {f.ingredient} ({f.issue}): {f.reasoning}")

        self.assertEqual(len(result['dietary_flags']), 2)
        ingredients_flagged = [f.ingredient for f in self.state.dietary_flags]
        self.assertIn("1 egg", ingredients_flagged)
        self.assertIn("3 tablespoons butter", ingredients_flagged)

    def test_dietary_filter_flags(self):
        """Test that a single avoided ingredient is flagged correctly."""
        mock_llm = MagicMock()
        mock_llm.client.models.generate_content.return_value.candidates = [
            MagicMock(content=MagicMock(parts=[MagicMock(text='[{"ingredient": "1 egg", "issue": "Avoided ingredient", "reasoning": "Egg is to be avoided."}]')] ))
        ]
        agent = DietaryFilterAgent(mock_llm)
        result = agent.run(self.state)

        # Print flagged ingredient
        print("\n[Dietary Filter Test] Flagged Ingredient:")
        for f in self.state.dietary_flags:
            print(f"- {f.ingredient} ({f.issue}): {f.reasoning}")

        self.assertEqual(len(result['dietary_flags']), 1)
        self.assertEqual(self.state.dietary_flags[0].ingredient, "1 egg")

    def test_substitution_applied(self):
        """Test that the substitution agent correctly applies the top substitution for flagged ingredients."""
        self.state.dietary_flags = [Flag(ingredient="1 egg", issue="Avoided ingredient", reasoning="Egg is to be avoided.")]

        mock_llm = MagicMock()
        mock_llm.client.models.generate_content.return_value.candidates = [
            MagicMock(content=MagicMock(parts=[MagicMock(text='[{"original": "1 egg","suggestion": "1 flax egg","reasoning": "Binder substitute."}]')] ))
        ]

        agent = SubstitutionAgent(mock_llm)
        agent.run(self.state)

        # Print the updated recipe ingredients
        print("\n[Substitution Test] Updated Ingredients:")
        for ing in self.state.remix_input_recipe.ingredients:
            print(f"- {ing}")

        ingredients = [ing for ing in self.state.remix_input_recipe.ingredients]
        self.assertIn("1 flax egg", ingredients)

    def test_no_flags_skips_substitution(self):
        """Test that the substitution agent does nothing if there are no flagged ingredients."""
        self.state.dietary_flags = []
        agent = SubstitutionAgent(MagicMock())
        result = agent.run(self.state)

        # Print the substitutions list (should be empty)
        print("\n[No Flags Test] Substitutions Applied:")
        print(result['substitutions'])

        self.assertEqual(result['substitutions'], [])

if __name__ == "__main__":
    unittest.main()
