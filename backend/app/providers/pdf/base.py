from abc import ABC, abstractmethod
from typing import Any, Dict


class PDFWorkerProvider(ABC):
    """
    Provider abstraction boundary for PDF/LaTeX document processing in future phases of PaperFox.
    Do NOT implement actual LaTeX compilation or mock PDF bytes in Phase 1.
    """

    @abstractmethod
    async def compile_latex_to_pdf(self, latex_content: str) -> bytes:
        """Compile raw LaTeX string into a one-page PDF binary."""
        pass

    @abstractmethod
    async def validate_ats_compatibility(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Verify ATS compatibility, text extractability, and single-page layout bounds."""
        pass
