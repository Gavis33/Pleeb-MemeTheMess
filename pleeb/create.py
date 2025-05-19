from pydub import AudioSegment
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from . import base_dir

bleep_sound = AudioSegment.from_mp3(base_dir + "/sounds/bleep.mp3")

def clean_word(word: str) -> str:
    return "".join(char for char in word if char.isalnum()).lower().strip()

def query_transcript(bleep_words: list, timestamped_transcript: list) -> list:
    transcript_words = [word for segment in timestamped_transcript for word in segment["words"]]
    detected = []

    for bleep_word in bleep_words:
        for word in transcript_words:
            if clean_word(word["text"]) == clean_word(bleep_word):
                detected.append(word)

    return sorted(detected, key=lambda x: x["start"])

def replace_bleep(
    og_video_path: str, og_audio_path: str,
    final_video_path: str, final_audio_path: str,
    bleep_words: list, timestamped_transcript: list,
):
    test_sound = AudioSegment.from_mp3(og_audio_path)
    bleep_word_instances = query_transcript(bleep_words, timestamped_transcript)

    test_sound_clips = []
    prev_end_time = 0

    for instance in bleep_word_instances:
        start_time = int(instance["start"] * 1000) - 50
        end_time = int(instance["end"] * 1000) + 50

        # Prevent negative index
        start_time = max(start_time, 0)

        test_clip = test_sound[prev_end_time:start_time]
        duration = end_time - start_time
        bleep_clip = (bleep_sound * ((duration // len(bleep_sound)) + 1))[:duration]

        test_sound_clips.append(test_clip)
        test_sound_clips.append(bleep_clip)

        prev_end_time = end_time

    test_sound_clips.append(test_sound[prev_end_time:])
    final_audio = sum(test_sound_clips)
    final_audio.export(final_audio_path, format="mp3")

    og_video = VideoFileClip(og_video_path)
    bleep_audio = AudioFileClip(final_audio_path)
    og_video.audio = CompositeAudioClip([bleep_audio])

    og_video.write_videofile(
        final_video_path,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
    )

    og_video.close()
    bleep_audio.close()
