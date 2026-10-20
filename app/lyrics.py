"""Split lyrics into scene-sized units (one clip per sentence / line)."""
import re

_SENTENCE_RE = re.compile(r"(?<=[.!?…])\s+|(?<=[.!?…])$")
_ABBREV = re.compile(
    r"\b(?:Mr|Mrs|Ms|Dr|Jr|Sr|vs|etc|St|Ave|Rd|No|Vol)\.$", re.IGNORECASE,
)


def split_lyric_units(lyrics: str) -> list[str]:
    """Prefer non-empty lines (typical lyric layout). If the whole text is one
    paragraph, fall back to sentence boundaries."""
    text = (lyrics or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return []

    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    # Chorus markers / section headers like [Verse 1] — keep as notes only if
    # they look like real lyric content (not bracket-only tags).
    lines = [ln for ln in lines if not re.fullmatch(r"[\[\(].+[\]\)]", ln)]

    if len(lines) > 1:
        units: list[str] = []
        for ln in lines:
            parts = _sentences(ln)
            units.extend(parts if parts else [ln])
        return units

    return _sentences(text) or [text]


def _sentences(paragraph: str) -> list[str]:
    # Protect common abbreviations so "Dr. Feelgood" doesn't split.
    protected = paragraph
    swaps: list[tuple[str, str]] = []
    for i, m in enumerate(_ABBREV.finditer(paragraph)):
        token = f"«ABBREV{i}»"
        swaps.append((token, m.group(0)))
        protected = protected[: m.start()] + token + protected[m.end() :]

    raw = [p.strip() for p in re.split(r"(?<=[.!?…])\s+", protected) if p.strip()]
    out = []
    for part in raw:
        for token, original in swaps:
            part = part.replace(token, original)
        out.append(part)
    return out


def visual_prompt_for_line(lyric: str, style: str = "") -> str:
    """Draft a video prompt: visualize the line, don't just flash the words on screen."""
    style_bit = f" Visual style: {style.strip()}." if style and style.strip() else ""
    return (
        f"Cinematic music-video shot that visually expresses this lyric "
        f"(do not render the words as on-screen text): \"{lyric.strip()}\".{style_bit} "
        f"Clear subject, motivated camera move, emotional lighting, continuous motion."
    )
