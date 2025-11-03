from agents.recipe_agent import RecipeAgent
from data_models import OriginalRecipe, WorkflowState
from typing import Dict, Any
from recipe_scrapers import scrape_me

class ScraperAgent(RecipeAgent):
    """Fetches a recipe from a URL and extracts structured ingredients and steps."""
    def run(self, state: WorkflowState) -> Dict[str, Any]:
        url = state.url
        self.add_log(state, "ScraperAgent", f"Starting scrape for URL: {url}")
        
        try:
            scraper = scrape_me(url)
            
            recipe_data = OriginalRecipe(
                title=scraper.title(),
                ingredients=scraper.ingredients(),
                steps=scraper.instructions_list()
            )
            
            state.original_recipe = recipe_data
            
            self.add_log(state, "ScraperAgent", f"Scraped '{recipe_data.title}' successfully.")
            
        except Exception as e:
            self.add_log(state, "ScraperAgent", f"FATAL ERROR: Scraping failed. Check URL or scraper library. Error: {e}")
            state.original_recipe = None 

        return state.model_dump()