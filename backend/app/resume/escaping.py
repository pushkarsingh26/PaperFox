import re


# Unicode character replacement map for pdflatex inputenc compatibility
_UNICODE_REPLACEMENTS = {
    "\u200b": "",      # Zero-width space
    "\u200c": "",      # Zero-width non-joiner
    "\u200d": "",      # Zero-width joiner
    "\ufeff": "",      # Byte order mark (BOM)
    "\u200e": "",      # Left-to-right mark
    "\u200f": "",      # Right-to-left mark
    "\xa0": " ",       # Non-breaking space
    "‘": "'",          # Left single quotation mark
    "’": "'",          # Right single quotation mark / apostrophe
    "“": '"',          # Left double quotation mark
    "”": '"',          # Right double quotation mark
    "–": "-",          # Standard hyphen for ATS compatibility
    "—": " -- ",       # Em-dash
    "…": r"\dots{}",   # Horizontal ellipsis
    "≤": r"$\le$",     # Less than or equal to
    "≥": r"$\ge$",     # Greater than or equal to
    "≠": r"$\neq$",    # Not equal to
    "→": r"$\rightarrow$", # Rightwards arrow
    "←": r"$\leftarrow$",  # Leftwards arrow
    "±": r"$\pm$",     # Plus-minus sign
    "°": r"^\circ ",   # Degree sign
    "™": r"\texttrademark{}",
    "®": r"\textregistered{}",
    "©": r"\textcopyright{}",
}


def escape_latex(text: str) -> str:
    """
    Safely escape LaTeX special characters and sanitize Unicode characters for pdflatex.
    Handles &, %, $, #, _, {, }, ~, ^, \\ as well as problematic Unicode characters.
    """
    if not text:
        return ""

    # Step 1: Pre-process and replace problematic Unicode characters
    for char, replacement in _UNICODE_REPLACEMENTS.items():
        if char in text:
            text = text.replace(char, replacement)

    # Step 2: Character map for single-pass regex replacement of TeX special characters
    chars = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    regex = re.compile(r"[" + re.escape("".join(chars.keys())) + r"]")
    return regex.sub(lambda match: chars[match.group(0)], text)


def format_latex_url(url_str: str, label: str = "") -> str:
    """
    Formats a URL for LaTeX hyperref without corrupting the web address.
    """
    if not url_str:
        return ""

    clean_url = url_str.strip()
    if not clean_url.startswith(("http://", "https://", "mailto:")):
        clean_url = f"https://{clean_url}"

    display_label = escape_latex(label or url_str)
    return f"\\href{{{clean_url}}}{{{display_label}}}"


def strip_latex_bold(text: str) -> str:
    """
    Strips markdown bold (**word** or __word__) and LaTeX \\textbf{word} wrappers
    from text to ensure bullets remain strictly normal-weight.
    """
    if not text:
        return ""
    # Strip markdown **bold** or __bold__
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    # Strip LaTeX \textbf{word}
    text = re.sub(r"\\textbf\{(.*?)\}", r"\1", text)
    return text
