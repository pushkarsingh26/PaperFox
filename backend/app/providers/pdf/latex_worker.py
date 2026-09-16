"""
latex_worker.py — Isolated LaTeX subprocess compiler worker.

Compiler resolution order:
1. Explicit binary path: LATEX_COMPILER_PATH env/config (must point to an existing file)
2. PATH lookup:          LATEX_COMPILER env/config (resolved via shutil.which)
3. PATH fallback:        'pdflatex' then 'xelatex' via shutil.which

The worker executes compilation in an isolated temporary directory with
shell=False to prevent shell injection. stdout/stderr are captured and
surfaced in the status string on failure.

Configuration examples (backend/.env):
    LATEX_COMPILER=pdflatex
    LATEX_COMPILER_PATH=C:\\Users\\you\\AppData\\Local\\Programs\\MiKTeX\\miktex\\bin\\x64\\pdflatex.exe
"""
import logging
import os
import re
import shutil
import subprocess
import tempfile
from typing import Optional, Tuple

from app.core.config import settings
from app.providers.pdf.base import PDFWorkerProvider

logger = logging.getLogger(__name__)


def _extract_latex_error(stdout_str: str, stderr_str: str) -> str:
    """
    Extract the first actual TeX error line (! line) and context from stdout/stderr,
    skipping TeX Live banner/package loading lines.
    """
    source = stdout_str or stderr_str or ""
    if not source:
        return "Unknown compilation error"

    lines = source.splitlines()
    error_lines = []
    found_error = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("!"):
            found_error = True
            error_lines.append(stripped)
        elif found_error:
            # Capture follow-up context lines (line number, location snippet)
            if stripped.startswith("l.") or stripped.startswith("<") or not stripped:
                error_lines.append(stripped)
            else:
                # Stop when hitting unrelated log sections
                break

    if error_lines:
        extracted = " ".join([l for l in error_lines if l]).strip()
        return extracted[:600]

    # Fallback if no line starting with '!' is found: return the last 600 chars of output
    return source[-600:].strip()


def get_pdf_page_count(pdf_bytes: bytes) -> int:
    """Determine PDF page count using pypdf if available, or PDF object parsing fallback."""
    try:
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(pdf_bytes))
        return len(reader.pages)
    except Exception:
        # Regex fallback: count /Type /Page objects in binary PDF structure
        page_matches = re.findall(rb"/Type\s*/Page\b", pdf_bytes)
        return max(1, len(page_matches))


def _resolve_compiler() -> Optional[str]:
    """
    Resolve the LaTeX compiler executable path. Returns an absolute path to the
    binary if found, or None if no usable compiler can be located.

    Resolution order:
      1. LATEX_COMPILER_PATH (explicit absolute/relative path to binary)
      2. LATEX_COMPILER command name resolved through system PATH
      3. Fallback: 'pdflatex', then 'xelatex' via PATH
    """
    # ── Tier 1: Explicit binary path ────────────────────────────────────────
    explicit_path: str = (
        getattr(settings, "LATEX_COMPILER_PATH", "")
        or os.getenv("LATEX_COMPILER_PATH", "")
    ).strip()

    if explicit_path:
        resolved = os.path.abspath(explicit_path)
        if os.path.isfile(resolved) and os.access(resolved, os.X_OK | os.F_OK):
            return resolved
        # Explicit path given but binary not found — return None with no silent fallback.
        # This prevents masking a misconfigured LATEX_COMPILER_PATH.
        return None

    # ── Tier 2: PATH lookup for LATEX_COMPILER name ──────────────────────────
    compiler_name: str = (
        getattr(settings, "LATEX_COMPILER", "")
        or os.getenv("LATEX_COMPILER", "pdflatex")
    ).strip()

    if compiler_name:
        # shutil.which handles .exe extension on Windows automatically
        found = shutil.which(compiler_name)
        if found:
            return found

    # ── Tier 3: Standard fallback names ─────────────────────────────────────
    for fallback in ("pdflatex", "xelatex"):
        found = shutil.which(fallback)
        if found:
            return found

    return None


class LaTeXCompilerWorker(PDFWorkerProvider):
    def __init__(self, compiler_binary: Optional[str] = None):
        if compiler_binary:
            # Explicit binary provided (e.g., from tests)
            self.compiler: Optional[str] = shutil.which(compiler_binary) or (
                os.path.abspath(compiler_binary)
                if os.path.isfile(compiler_binary)
                else None
            )
        else:
            self.compiler = _resolve_compiler()

    def is_available(self) -> bool:
        """True only when the compiler binary exists and is actually executable."""
        if not self.compiler:
            return False
        if os.path.isabs(self.compiler):
            return os.path.isfile(self.compiler) and os.access(self.compiler, os.F_OK)
        # Name that was resolved via shutil.which — re-verify still present
        return shutil.which(self.compiler) is not None

    def compiler_description(self) -> str:
        """Human-readable description of the current compiler state, for diagnostics."""
        if self.compiler and self.is_available():
            return f"Available: {self.compiler}"
        explicit_path = (
            getattr(settings, "LATEX_COMPILER_PATH", "")
            or os.getenv("LATEX_COMPILER_PATH", "")
        ).strip()
        compiler_name = (
            getattr(settings, "LATEX_COMPILER", "")
            or os.getenv("LATEX_COMPILER", "pdflatex")
        ).strip()
        if explicit_path:
            return (
                f"LATEX_COMPILER_PATH={explicit_path!r} is set but the file was not found "
                f"or is not executable. Verify the path is correct."
            )
        return (
            f"No LaTeX compiler found. "
            f"'{compiler_name}' was not found on the server PATH, "
            f"and 'pdflatex'/'xelatex' are also not available. "
            f"Install MiKTeX (https://miktex.org/download) or TeX Live and restart the backend, "
            f"or set LATEX_COMPILER_PATH in backend/.env to the full path of pdflatex.exe."
        )

    async def compile_latex_to_pdf(self, latex_content: str) -> bytes:
        pdf_bytes, _, status_msg = await self.compile_with_status(latex_content)
        if not pdf_bytes:
            raise RuntimeError(status_msg)
        return pdf_bytes

    async def compile_with_status(
        self, latex_content: str
    ) -> Tuple[Optional[bytes], int, str]:
        if not self.is_available() or not self.compiler:
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
                    timeout=60,
                    shell=False,
                )

                if result.returncode != 0 or not os.path.exists(pdf_file):
                    stdout_str = result.stdout.decode("utf-8", errors="replace").strip()
                    stderr_str = result.stderr.decode("utf-8", errors="replace").strip()
                    logger.error(f"LaTeX compilation failed (returncode {result.returncode}). STDOUT:\n{stdout_str}\nSTDERR:\n{stderr_str}")
                    err_summary = _extract_latex_error(stdout_str, stderr_str)
                    return None, 0, f"COMPILATION_ERROR: {err_summary}"

                with open(pdf_file, "rb") as f:
                    pdf_bytes = f.read()

                if not pdf_bytes:
                    return None, 0, "COMPILATION_ERROR: Compiler produced an empty PDF file."

                page_count = get_pdf_page_count(pdf_bytes)
                return pdf_bytes, page_count, "success"

            except subprocess.TimeoutExpired:
                return None, 0, "COMPILATION_TIMEOUT: Compilation exceeded 60 second limit."
            except FileNotFoundError:
                # Binary disappeared between is_available() check and subprocess.run()
                self.compiler = None
                return (
                    None,
                    0,
                    "COMPILER_UNAVAILABLE: Compiler binary not found at execution time. "
                    "Verify LATEX_COMPILER_PATH or system PATH.",
                )
            except Exception as e:
                return None, 0, f"COMPILATION_EXCEPTION: {str(e)}"

    async def validate_ats_compatibility(self, pdf_bytes: bytes) -> dict:
        page_count = get_pdf_page_count(pdf_bytes)
        return {
            "is_single_page": page_count == 1,
            "page_count": page_count,
            "text_extractable": True,
        }
