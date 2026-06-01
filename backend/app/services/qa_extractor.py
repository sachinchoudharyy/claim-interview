from groq import Groq
from app.core.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def extract_qa(transcript):

    prompt = f"""
Convert this interview conversation into Q&A format.

Transcript:
{transcript}

Return JSON like:
[
{{"question":"...", "answer":"..."}}
]
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content