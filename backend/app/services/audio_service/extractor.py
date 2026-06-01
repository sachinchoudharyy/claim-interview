import ffmpeg
import os

def extract_audio(video_path, output_path):
    """
    Extract mono 16kHz WAV audio from video using ffmpeg.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    (
        ffmpeg
        .input(video_path)
        .output(
            output_path,
            format='wav',
            ac=1,
            ar='16000'
        )
        .overwrite_output()
        .run(quiet=True)
    )
    
    return output_path
