from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Flag(BaseModel):
    """Structured flag for a dietary issue."""
    ingredient: str = Field(description="The ingredient found with an issue.")
    issue: str = Field(description="The dietary issue (e.g., 'Non-vegan dairy').")
    reasoning: str = Field(description="Why this ingredient is flagged.")
    
class Substitution(BaseModel):
    """Structured replacement suggestion."""
    original: str
    suggestion: str
    reasoning: str
    prep: Optional[str] = None

class OriginalRecipe(BaseModel):
    """Structured recipe parsed from url"""
    title: str
    ingredients: List[str]
    steps: List[str]

# Workflow State Model
class WorkflowState(BaseModel):
    """The central state object passed between all agents."""
    url: str
    
    # Populated data
    original_recipe: Optional[OriginalRecipe] = None
    
    # User defined filters
    dietary_filters: List[str] = []    

    # Conflicting ingredients
    dietary_flags: List[Flag] = Field(default_factory=list)
    
    # Substitutions provided by LLM
    substitutions: List[Substitution] = Field(default_factory=list)
    
    # Recipe versions
    remix_input_recipe: Optional[OriginalRecipe] = None 
    remixed_recipe: Optional[Dict[str, Any]] = None      
    
    # Logging and Control
    reasoning_trace: List[Dict[str, Any]] = Field(default_factory=list)
    run_count: int = 0