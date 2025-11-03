# Recipe Remix Workflow

This project is a modular recipe adjustment workflow that allows users to input a recipe URL and specify dietary restrictions or ingredients to avoid. The workflow scrapes the recipe, flags conflicting ingredients, suggests substitutions using an LLM, and adjusts the recipe steps accordingly.

---

## Features

- Scrapes recipes from URLs.
- Detects user-specified dietary restrictions or allergens.
- Suggests ingredient substitutions using a language model (Gemini API).
- Adjusts recipe steps to incorporate substitutions.
- Provides a reasoning trace log for all adjustments.

---

## Agents

1. **ScraperAgent**  
   Scrapes recipes from a given URL and outputs structured recipe data.

2. **DietaryFilterAgent**  
   Flags ingredients based on user-specified avoided ingredients or broader dietary restrictions (e.g., non-vegan).

3. **SubstitutionAgent**  
   Suggests up to 3 replacements for each flagged ingredient using an LLM. Stores reasoning and optionally prep instructions.

4. **StepAdjustmentAgent**  
   Adjusts recipe steps to integrate substitutions. Can either replace the ingredient name or add a prep step if necessary.

---

## Workflow

The workflow graph is linear, with the refined outputs of previous steps directly affecting the next one

```bash
User input (URL + restrictions)
        ↓
ScraperAgent
        ↓
DietaryFilterAgent (flags ingredients + reasoning)
        ↓
SubstitutionAgent (suggestions + reasoning)
        ↓
StepAdjustmentAgent (final recipe steps)
        ↓
Final Recipe + Substitutions + Reasoning Log
```

Each agent logs its decisions in the reasoning trace, which provides full transparency for every change made to the recipe.

## Testing
Start a virtual environment then run pytest with optional `-s` flag if you want to see printed results

```bash
venv\Scripts\activate

python -m pytest -s tests/
```

## Usage

0. **Ensure you have python installed and your cli works. Clone the repository.**
1. **Set up API key in .env**

    ```bash
    #.env

    GEMINI_API_KEY="useyoursecretapikeyhere"
    ```
  
    I used Gemini because it has the most forgiving free tier as of November 2025. Feel free to adapt it to any other API key.

2. **Activate your virtual environment**
  
    ```bash
    # Windows
    venv\Scripts\activate

    # macOS/Linux
    source venv/bin/activate
    ```

3. **Run Python workflow**
  
    ```bash
    python main.py  
    ```

    Then, when prompted, input your recipe URL and restrictions.

    ```bash
    === Recipe Remix ===
    Enter the recipe URL: https://www.allrecipes.com/recipe/21014/good-old-fashioned-pancakes/
    Enter ingredients to avoid (comma-separated): egg, butter
    ```

    Note: you can also input vague terms, e.g if you want to avoid nonvegan items
  
    ```bash
    === Recipe Remix ===
    Enter the recipe URL: https://www.allrecipes.com/recipe/21014/good-old-fashioned-pancakes/
    Enter ingredients to avoid (comma-separated): nonvegan
    ```

## Example output

```bash
Workflow Complete:

## Final Recipe Ingredients:
- 1.5 cups all-purpose flour
- 3.5 teaspoons baking powder
- 1 tablespoon white sugar
- 0.25 teaspoon salt, or more to taste
- 1.25 cups milk
- 3 tablespoons butter, melted
- 1 'flax egg' (1 tbsp ground flaxseed mixed with 3 tbsp water, let sit 5 mins)

## Recipe Steps:
1. Gather all ingredients.
2. Prepare the flax egg: In a small bowl, combine 1 tablespoon ground flaxseed with 3 tablespoons water and let it sit for 5 minutes to thicken.
3. Sift flour, baking powder, sugar, and salt together in a large bowl. Make a well in the center and add milk, melted butter, and the prepared flax egg; mix until smooth.
4. Heat a lightly oiled griddle or pan over medium-high heat. Pour or scoop the batter onto the griddle, using approximately 1/4 cup for each pancake; cook until bubbles form and the edges are dry, about 2 to 3 minutes.
5. Flip and cook until browned on the other side. Repeat with remaining batter.
6. Serve and enjoy!

## Substitution Summary

Original Ingredient: 1 egg
  → Top Recommendation: 1 'flax egg' (1 tbsp ground flaxseed mixed with 3 tbsp water, let sit 5 mins)
    Reasoning: This mixture forms a gelatinous texture that effectively binds ingredients together, mimicking the adhesive properties of an egg. It also adds some moisture and fiber to the recipe.
  → Other Possible Substitutions:
    - 1/4 cup mashed ripe banana: Ripe bananas are naturally moist and sticky, making them an excellent binder and source of moisture in baked goods. Be aware that it will impart a banana flavor and some sweetness to the dish.
    - 1/4 cup unsweetened applesauce: Applesauce adds moisture and acts as a binder due to its pectin content, helping to hold ingredients together. Using unsweetened ensures it doesn't drastically alter the recipe's intended sweetness.


## Reasoning Trace Log
[
  {
    "agent": "ScraperAgent",
    "timestamp": "2025-11-02T22:40:13.970826",
    "message": "Starting scrape for URL: https://www.allrecipes.com/recipe/21014/good-old-fashioned-pancakes/"
  },
  ...
```

---
