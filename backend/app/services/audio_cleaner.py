from app.core.constants import TRANSCRIPT_BLACKLIST


def clean_transcript(text: str) -> str:

    if not text:
        return ""

    text = text.strip().lower()

    for phrase in TRANSCRIPT_BLACKLIST:
        if phrase in text:
            return ""

    return text.strip()