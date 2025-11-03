from data_models import WorkflowState
from typing import Any, Dict
import datetime

class RecipeAgent:
    """Base class for all agents..."""
    
    def __init__(self, llm_model: Any):
        self.llm = llm_model

    def add_log(self, state: WorkflowState, agent_name: str, message: str) -> None:
        """Adds a log entry to the cumulative reasoning trace in the state."""
        log_entry = {
            "agent": agent_name, 
            "timestamp": datetime.datetime.now().isoformat(), 
            "message": message
        }
        state.reasoning_trace.append(log_entry) 
        
    def run(self, state: WorkflowState) -> Dict[str, Any]:
        """Abstract run method to be implemented by children."""
        raise NotImplementedError("Subclasses must implement the run method.")