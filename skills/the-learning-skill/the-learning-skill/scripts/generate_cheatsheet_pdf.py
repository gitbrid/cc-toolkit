#!/usr/bin/env python3
"""Generate a printable PDF cheatsheet from a Markdown source.

Produces a print-formatted PDF (0.5" margins, multi-page allowed) suitable
for printing or carrying as a reference card.

Backend auto-detection (in priority order):
    1. Chrome / Chromium headless         (best fidelity, widely available)
    2. weasyprint (Python package)        (clean, no GUI dep)
    3. wkhtmltopdf                        (legacy fallback)

If no backend is available, the script writes the styled HTML next to the
intended PDF path and prints platform-specific install instructions, then
exits non-zero. Do not silently skip — install one and re-run.

Usage:
    python generate_cheatsheet_pdf.py --input notes.md --output cheatsheet.pdf --title "Postgres WAL"
    cat notes.md | python generate_cheatsheet_pdf.py --stdin --output cheatsheet.pdf --title "Postgres WAL"
    python generate_cheatsheet_pdf.py --dir ./rust-bootcamp-20260507-1430/ownership/
        # reads notes.md inside the dir, writes cheatsheet.pdf there
"""

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import markdown as md_lib
except ImportError:
    md_lib = None


CHROME_CANDIDATES = [
    # macOS
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    # Linux
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "microsoft-edge",
    # Windows (when run under WSL or Git Bash)
    "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
    "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
]


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  @page {{
    size: letter;
    margin: 0.5in;
  }}
  html, body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #111;
    margin: 0;
    padding: 0;
  }}
  .sheet {{
    /* @page handles page margins; no extra body padding needed */
  }}
  h1 {{
    font-size: 18pt;
    margin: 0 0 4pt 0;
    border-bottom: 2px solid #111;
    padding-bottom: 4pt;
    page-break-after: avoid;
  }}
  h2 {{
    font-size: 13pt;
    margin: 14pt 0 4pt 0;
    border-bottom: 1px solid #888;
    padding-bottom: 2pt;
    page-break-after: avoid;
  }}
  h3 {{
    font-size: 11.5pt;
    margin: 10pt 0 3pt 0;
    page-break-after: avoid;
  }}
  h4 {{
    font-size: 10.5pt;
    margin: 8pt 0 2pt 0;
    font-weight: 700;
    page-break-after: avoid;
  }}
  p, ul, ol {{
    margin: 4pt 0;
  }}
  ul, ol {{
    padding-left: 18pt;
  }}
  li {{
    margin: 1pt 0;
  }}
  code {{
    font-family: "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
    font-size: 9.5pt;
    background: #f2f2f2;
    padding: 1pt 3pt;
    border-radius: 2pt;
  }}
  pre {{
    font-family: "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
    font-size: 9pt;
    background: #f6f6f6;
    border: 1px solid #ddd;
    border-radius: 3pt;
    padding: 6pt 8pt;
    overflow: auto;
    page-break-inside: avoid;
  }}
  pre code {{
    background: transparent;
    padding: 0;
  }}
  blockquote {{
    border-left: 3px solid #888;
    margin: 6pt 0;
    padding: 2pt 10pt;
    color: #444;
    background: #fafafa;
    page-break-inside: avoid;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 6pt 0;
    page-break-inside: avoid;
    font-size: 9.5pt;
  }}
  th, td {{
    border: 1px solid #bbb;
    padding: 3pt 5pt;
    text-align: left;
    vertical-align: top;
  }}
  th {{
    background: #efefef;
  }}
  hr {{
    border: 0;
    border-top: 1px solid #bbb;
    margin: 10pt 0;
  }}
  .meta {{
    color: #666;
    font-size: 9pt;
    margin-bottom: 8pt;
  }}
  /* Avoid orphaned headings */
  h1, h2, h3, h4 {{ break-after: avoid-page; }}
</style>
</head>
<body>
<div class="sheet">
{body}
</div>
</body>
</html>
"""


def render_markdown_to_html(md_text: str) -> str:
    if md_lib is None:
        raise SystemExit(
            "Error: the `markdown` Python package is required.\n"
            "Install it with:\n"
            "    python3 -m pip install markdown\n"
        )
    return md_lib.markdown(
        md_text,
        extensions=["extra", "tables", "fenced_code", "sane_lists", "toc"],
        output_format="html5",
    )


def find_chrome() -> str | None:
    for c in CHROME_CANDIDATES:
        if "/" in c or "\\" in c:
            if Path(c).exists():
                return c
        else:
            found = shutil.which(c)
            if found:
                return found
    return None


def have_weasyprint() -> bool:
    try:
        import weasyprint  # noqa: F401
        return True
    except Exception:
        return False


def have_wkhtmltopdf() -> bool:
    return shutil.which("wkhtmltopdf") is not None


def install_instructions() -> str:
    sysname = platform.system()
    lines = [
        "No PDF backend was found. Install one of the following and re-run:",
        "",
    ]
    if sysname == "Darwin":
        lines += [
            "  macOS — easiest option (Google Chrome):",
            "    Download from https://www.google.com/chrome/  (or `brew install --cask google-chrome`)",
            "",
            "  macOS — alternatives:",
            "    brew install --cask chromium",
            "    python3 -m pip install weasyprint",
            "    brew install --cask wkhtmltopdf",
        ]
    elif sysname == "Linux":
        lines += [
            "  Linux — Chromium (Debian/Ubuntu):",
            "    sudo apt-get update && sudo apt-get install -y chromium-browser",
            "  Linux — Chromium (Fedora/RHEL):",
            "    sudo dnf install -y chromium",
            "  Linux — Chromium (Arch):",
            "    sudo pacman -S chromium",
            "",
            "  Linux — alternatives:",
            "    python3 -m pip install weasyprint",
            "    sudo apt-get install -y wkhtmltopdf  # Debian/Ubuntu",
        ]
    elif sysname == "Windows":
        lines += [
            "  Windows — easiest option (Google Chrome):",
            "    Download from https://www.google.com/chrome/",
            "",
            "  Windows — alternatives:",
            "    winget install --id Google.Chrome -e",
            "    winget install --id wkhtmltopdf.wkhtmltox -e",
            "    py -m pip install weasyprint",
        ]
    else:
        lines += [
            f"  Detected platform: {sysname}",
            "  Install Google Chrome / Chromium, weasyprint, or wkhtmltopdf.",
        ]
    lines += [
        "",
        "After installing, re-run the same command. The styled HTML has been",
        "saved alongside the intended PDF path so you can also print it manually",
        "from a browser (Cmd/Ctrl + P → Save as PDF, Margins: 0.5in).",
    ]
    return "\n".join(lines)


def render_with_chrome(chrome_bin: str, html_path: Path, pdf_path: Path) -> bool:
    cmd = [
        chrome_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--no-margins",  # ignored; @page in CSS controls margins
        f"--print-to-pdf={pdf_path}",
        html_path.resolve().as_uri(),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Chrome render failed: {e}", file=sys.stderr)
        # Retry with old --headless flag in case --headless=new is unsupported
        cmd[1] = "--headless"
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except Exception as e2:
            print(f"Chrome render failed (retry): {e2}", file=sys.stderr)
            return False
    if result.returncode != 0:
        # Some Chrome builds reject --headless=new; retry with old flag.
        if "--headless=new" in cmd:
            cmd[1] = "--headless"
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return False
    return pdf_path.exists()


def render_with_weasyprint(html_path: Path, pdf_path: Path) -> bool:
    try:
        from weasyprint import HTML  # type: ignore
        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        return pdf_path.exists()
    except Exception as e:
        print(f"weasyprint render failed: {e}", file=sys.stderr)
        return False


def render_with_wkhtmltopdf(html_path: Path, pdf_path: Path) -> bool:
    cmd = [
        "wkhtmltopdf",
        "--margin-top", "0.5in",
        "--margin-right", "0.5in",
        "--margin-bottom", "0.5in",
        "--margin-left", "0.5in",
        "--enable-local-file-access",
        str(html_path),
        str(pdf_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except Exception as e:
        print(f"wkhtmltopdf failed: {e}", file=sys.stderr)
        return False
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return False
    return pdf_path.exists()


def slug_from(s: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in s.lower())[:60].strip("-")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", type=Path, help="Markdown file to render")
    src.add_argument("--stdin", action="store_true", help="Read markdown from stdin")
    src.add_argument("--dir", type=Path, help="Run-directory containing notes.md; output goes alongside it")
    p.add_argument("--output", type=Path, help="Output PDF path (default: cheatsheet.pdf next to input)")
    p.add_argument("--title", default="Cheatsheet", help="Document title")
    p.add_argument("--keep-html", action="store_true", help="Keep the intermediate HTML next to the PDF")
    args = p.parse_args()

    if args.dir:
        notes = args.dir / "notes.md"
        if not notes.exists():
            print(f"Error: {notes} not found", file=sys.stderr)
            return 1
        md_text = notes.read_text(encoding="utf-8")
        out_pdf = args.output or (args.dir / "cheatsheet.pdf")
    elif args.input:
        md_text = args.input.read_text(encoding="utf-8")
        out_pdf = args.output or args.input.with_name("cheatsheet.pdf")
    else:
        md_text = sys.stdin.read()
        if not args.output:
            print("Error: --output is required when reading from stdin", file=sys.stderr)
            return 1
        out_pdf = args.output

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    html_body = render_markdown_to_html(md_text)
    full_html = HTML_TEMPLATE.format(title=args.title, body=html_body)

    html_path = out_pdf.with_suffix(".html")
    html_path.write_text(full_html, encoding="utf-8")

    chrome = find_chrome()
    rendered = False
    backend_used = None
    if chrome:
        if render_with_chrome(chrome, html_path, out_pdf):
            rendered = True
            backend_used = f"chrome ({chrome})"
    if not rendered and have_weasyprint():
        if render_with_weasyprint(html_path, out_pdf):
            rendered = True
            backend_used = "weasyprint"
    if not rendered and have_wkhtmltopdf():
        if render_with_wkhtmltopdf(html_path, out_pdf):
            rendered = True
            backend_used = "wkhtmltopdf"

    if not rendered:
        print(f"Wrote HTML: {html_path}")
        print()
        print(install_instructions())
        return 2

    print(f"Wrote PDF:  {out_pdf}  (backend: {backend_used})")
    if args.keep_html:
        print(f"Wrote HTML: {html_path}")
    else:
        try:
            html_path.unlink()
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
