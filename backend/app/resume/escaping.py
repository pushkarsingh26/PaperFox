import re


def escape_latex(text: str) -> str:
    """
    Safely escape LaTeX special characters in user-provided text.
    Handles &, %, $, #, _, {, }, ~, ^, \\.
    """
    if not text:
        return ""

    # Character map for single-pass regex replacement
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
    if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
        clean_url = f"https://{clean_url}"

    display_label = escape_latex(label or url_str)
    return f"\\href{{{clean_url}}}{{{display_label}}}"
