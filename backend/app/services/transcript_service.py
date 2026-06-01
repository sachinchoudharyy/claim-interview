from app.db.supabase_client import supabase
from app.services.stt import transcribe
from app.services.qa_extractor import extract_qa
from app.services.audio_cleaner import clean_transcript
from app.services.vad_service import contains_speech
from app.core.constants import MIN_TRANSCRIPT_LENGTH


def process_audio_chunk(audio_bytes, interview_id):

    result = supabase.table("interviews") \
        .select("full_transcript, language") \
        .eq("id", interview_id) \
        .execute()

    current = result.data[0]["full_transcript"] or ""
    language = result.data[0]["language"] or "en"

    if not contains_speech(audio_bytes):
        return ""

    text = transcribe(audio_bytes, language)

    text = clean_transcript(text)

    if not text or len(text.strip()) < MIN_TRANSCRIPT_LENGTH:
        return ""

    updated = (current + " " + text).strip()

    supabase.table("interviews") \
        .update({"full_transcript": updated}) \
        .eq("id", interview_id) \
        .execute()

    return text


def finalize_transcript(interview_id):

    result = supabase.table("interviews") \
        .select("full_transcript") \
        .eq("id", interview_id) \
        .execute()

    transcript = result.data[0]["full_transcript"] or ""

    qa = extract_qa(transcript)

    supabase.table("interviews") \
        .update({"qa_script": qa}) \
        .eq("id", interview_id) \
        .execute()

    return qa