"""Assemble the self-contained Flowbit page.

Reads page/flowbit.src.html, inlines the Vistaar shell CSS, the Flowbit brand SVGs and images
(as data URIs), and the generated Momentum Ring SVGs, and writes flowbit.html.

Usage: python3 build.py
"""
import base64
import io
import math
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


# The Momentum Ring: four module arcs (ring-chart geometry from the Flowbit codebase: dark tracks,
# butt caps, drawn once) inside a thin brand-gradient orbit with a travelling light, the mark at the centre.
RINGS = [  # (module colour token, value %, spin duration, direction)
    ("var(--fb-orbit)", 78, "70s", "normal"),
    ("var(--fb-folio)", 64, "95s", "reverse"),
    ("var(--fb-work)", 71, "80s", "normal"),
    ("var(--fb-muster)", 90, "120s", "reverse"),
]


def momentum_ring(prefix: str, size: str) -> str:
    c, stroke = 100, 11
    radii = [82, 67, 52, 37]
    parts = [
        f'<div class="fb-mring" style="--size:{size}" role="img" aria-label="Momentum Ring: Orbit 78%, Folio 64%, Work 71%, Muster 90%">',
        '<svg viewBox="-4 -4 208 208" aria-hidden="true" focusable="false">',
        f'<defs><linearGradient id="{prefix}-orbit" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#f4e5f0"/><stop offset=".5" stop-color="#bb62a5"/><stop offset="1" stop-color="#3c2571"/></linearGradient></defs>',
        f'<circle cx="{c}" cy="{c}" r="97" fill="none" stroke="url(#{prefix}-orbit)" stroke-width="1.2" opacity=".75"/>',
        f'<g class="fb-mring__orbit"><circle cx="{c}" cy="3" r="3.2" fill="#ffffff"/><circle cx="{c}" cy="3" r="8" fill="#eac1dc" opacity=".25"/></g>',
    ]
    for i, ((color, value, dur, direction), r) in enumerate(zip(RINGS, radii)):
        sw = stroke - i * 0.6
        length = 2 * math.pi * r * value / 100
        parts.append(
            f'<g class="fb-mring__spin" style="--dur:{dur};--dir:{direction}"><g transform="rotate(-90 {c} {c})">'
            f'<circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="#505050" stroke-opacity=".55" stroke-width="{sw:.1f}"/>'
            f'<circle class="fb-mring__arc" style="--len:{length:.1f};--i:{i}" cx="{c}" cy="{c}" r="{r}" fill="none" '
            f'stroke="{color}" stroke-width="{sw:.1f}" stroke-linecap="butt"/>'
            "</g></g>"
        )
    parts.append("</svg>")
    parts.append(f'<span class="fb-mring__mark">{svg_inline(ASSETS / "flowbit-mark-gradient.svg", prefix + "-m")}</span>')
    parts.append("</div>")
    return "".join(parts)


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
        "@@MRING_TILE@@": momentum_ring("mr2", "120px"),
        "@@MRING_CTA@@": momentum_ring("mr3", "min(280px, 70vw)"),
    }
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
