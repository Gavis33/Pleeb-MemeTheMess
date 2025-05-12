from moviepy import VideoFileClip

def extract_audio(video_path: str, audio_path: str) -> None:
    try:
        video = VideoFileClip(video_path)
        audio = video.audio
        if audio is not None:
            audio.write_audiofile(audio_path)
            audio.close()
            video.close()
    except Exception as e:
        raise ValueError(f'Error extracting audio: {e}')