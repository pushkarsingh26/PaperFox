from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class LLMProvider(ABC):
    """
    Provider abstraction boundary for AI / LLM integrations in future phases of PaperFox.
    Do NOT implement actual AI models or mock responses in Phase 1.
    """

    @abstractmethod
    async def generate_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate raw text response from LLM."""
        pass

    @abstractmethod
    async def generate_structured_json(
        self, prompt: str, schema: Dict[str, Any], system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate structured JSON response conforming to schema."""
        pass
