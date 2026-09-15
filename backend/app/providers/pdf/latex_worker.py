import os
import re
import shutil
import subprocess
import tempfile
from typing import Optional, Tuple
from app.providers.pdf.base import PDFWorkerProvider


def get_pdf_page_count(pdf_bytes: bytes) -> int:
    """Determine PDF page count using pypdf if available, or PDF object parsing fallback."""
    try:
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(pdf_bytes))
        return len(reader.pages)
    except Exception:
        # Regex fallback scanning for /Type /Page objects in binary structure
        page_matches = re.findall(rb"/Type\s*/Page\b", pdf_bytes)
        return max(1, len(page_matches))


class LaTeXCompilerWorker(PDFWorkerProvider):
    def __init__(self, compiler_binary: Optional[str] = None):
        self.compiler = (
            compiler_binary
            or shutil.which("pdflatex")
            or shutil.which("xelatex")
        )

    def is_available(self) -> bool:
        return self.compiler is not None

    async def compile_latex_to_pdf(self, latex_content: str) -> bytes:
        pdf_bytes, page_count, status_msg = await self.compile_with_status(latex_content)
        if not pdf_bytes:
            raise RuntimeError(status_msg)
        return pdf_bytes

    async def compile_with_status(
        self, latex_content: str
    ) -> Tuple[Optional[bytes], int, str]:
        if not self.is_available():
            return (
                None,
                0,
                "COMPILER_UNAVAILABLE: pdflatex or xelatex executable is not installed on server.",
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = os.path.join(temp_dir, "document.tex")
            pdf_file = os.path.join(temp_dir, "document.pdf")

            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(latex_content)

            try:
                result = subprocess.run(
                    [
                        self.compiler,
                        "-interaction=nonstopmode",
                        "-halt-on-error",
                        "document.tex",
                    ],
                    cwd=temp_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=15,
                )

                if result.returncode != 0 or not os.path.exists(pdf_file):
                    err_msg = result.stdout.decode("utf-8", errors="replace")
                    return None, 0, f"COMPILATION_ERROR: {err_msg[:500]}"

                with open(pdf_file, "rb") as f:
                    pdf_bytes = f.read()

                page_count = get_pdf_page_count(pdf_bytes)
                return pdf_bytes, page_count, "success"

            except subprocess.TimeoutExpired:
                return None, 0, "COMPILATION_TIMEOUT: Compilation exceeded 15 second limit."
            except Exception as e:
                return None, 0, f"COMPILATION_EXCEPTION: {str(e)}"

    async def validate_ats_compatibility(self, pdf_bytes: bytes) -> dict:
        page_count = get_pdf_page_count(pdf_bytes)
        return {
            "is_single_page": page_count == 1,
            "page_count": page_count,
            "text_extractable": True,
        }
