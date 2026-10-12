"""Assemble the self-contained Flowbit page.

Reads page/flowbit.src.html, inlines the Vistaar shell CSS, the Flowbit brand SVGs and images
(as data URIs), and writes flowbit.html.

Usage: python3 build.py
"""
import base64
import io
import re
from pathlib import Path

ROOT = Path(__file__).parent
PAGE = ROOT / "page"
ASSETS = PAGE / "assets"
OUT = ROOT / "flowbit.html"


def data_uri(path: Path, max_width: int = 0, quality: int = 86) -> str:
    """Image -> WebP data URI (optionally downscaled) when Pillow is available, else the file as is."""
    raw = path.read_bytes()
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(raw))
        if max_width and img.width > max_width:
            img = img.resize((max_width, round(img.height * max_width / img.width)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, "WEBP", quality=quality, method=6)
        return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(path.suffix, "image/png")
        return f"data:{mime};base64," + base64.b64encode(raw).decode()


def svg_inline(path: Path, prefix: str, cls: str = "") -> str:
    """Brand SVG for inline use: decorative, ids namespaced so several copies can share the page."""
    svg = path.read_text()
    svg = re.sub(r"<title>.*?</title>\s*", "", svg, flags=re.S)
    svg = svg.replace(' role="img" aria-label="Flowbit"', ' aria-hidden="true" focusable="false"')
    for old in sorted(set(re.findall(r'id="([^"]+)"', svg))):
        svg = svg.replace(f'id="{old}"', f'id="{prefix}-{old}"').replace(f"url(#{old})", f"url(#{prefix}-{old})")
    if cls:
        svg = svg.replace("<svg ", f'<svg class="{cls}" ', 1)
    return svg.strip()


def main() -> None:
    html = (PAGE / "flowbit.src.html").read_text()
    shell_css = (PAGE / "vistaar-shell.css").read_text()
    replacements = {
        "/*@@SHELL_CSS@@*/": shell_css,
        "@@MARK_WHITE@@": svg_inline(ASSETS / "flowbit-mark.svg", "mw"),
        "@@APP_ICON@@": data_uri(ASSETS / "flowbit-app-icon.webp", max_width=400),
        "@@DASHBOARD@@": data_uri(ASSETS / "dashboard-home.jpg", max_width=2000, quality=84),
        "@@RIBBON_LEFT@@": data_uri(ASSETS / "onboarding-left-outer.png"),
        "@@RIBBON_RIGHT@@": data_uri(ASSETS / "onboarding-right-outer.png"),
        "@@LOGO_WHITE@@": svg_inline(ASSETS / "flowbit-logo-white.svg", "lw"),
    }
    for cover in sorted((ASSETS / "wiki-covers").glob("*.webp")):
        key = "@@COVER_" + cover.stem.upper().replace("-", "_") + "@@"
        replacements[key] = data_uri(cover)
    for key, value in replacements.items():
        if key not in html:
            raise SystemExit(f"placeholder missing: {key}")
        html = html.replace(key, value)
    leftover = re.findall(r"@@[A-Z_]+@@", html)
    if leftover:
        raise SystemExit(f"unreplaced placeholders: {leftover}")
    OUT.write_text(html)
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
