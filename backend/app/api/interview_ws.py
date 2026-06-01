from fastapi import APIRouter, WebSocket
from app.services.transcript_service import process_audio_chunk, finalize_transcript
from app.core.constants import AUDIO_SAMPLE_RATE, AUDIO_CHUNK_SECONDS

router = APIRouter()


@router.websocket("/ws/interview/{interview_id}")
async def interview_ws(ws: WebSocket, interview_id: str):

    await ws.accept()

    buffer = b""

    chunk_size = AUDIO_SAMPLE_RATE * AUDIO_CHUNK_SECONDS * 2

    try:

        while True:

            audio = await ws.receive_bytes()

            buffer += audio

            if len(buffer) < chunk_size:
                continue

            text = process_audio_chunk(buffer, interview_id)

            buffer = b""

            if text:

                await ws.send_json({
                    "type": "transcript",
                    "text": text
                })

    except Exception as e:

        print("WebSocket closed:", e)

    finally:

        if buffer:
            process_audio_chunk(buffer, interview_id)

        qa = finalize_transcript(interview_id)

        try:
            await ws.send_json({
                "type": "completed",
                "qa": qa
            })
        except:
            pass