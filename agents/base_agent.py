# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAgent(ABC):
    """Base class for all analysis agents."""

    def __init__(self, name: str):
        """
        Initialize base agent.

        Args:
            name: Name of the agent
        """
        self.name = name

    @abstractmethod
    def analyze(self, code: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze code and return analysis results.

        Args:
            code: Source code to analyze
            **kwargs: Additional parameters for analysis

        Returns:
            Dictionary containing:
                - score: Quality/security score (0-100)
                - issues: List of identified issues
                - summary: Summary of findings
        """
        raise NotImplementedError(f"{self.name} must implement analyze method")

    def get_name(self) -> str:
        """Get agent name."""
        return self.name

    def __repr__(self) -> str:
        """String representation of agent."""
        return f"{self.__class__.__name__}(name='{self.name}')"