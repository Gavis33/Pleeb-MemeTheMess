# TODO: Add the ability to use a custom sound
from pydub import AudioSegment
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip

from . import base_dir
from .audio_extractor import extract_audio

bleep_sound = AudioSegment.from_mp3(base_dir + "/sounds/bleep.mp3")
bleep_first_sec = bleep_sound[1000 : 2000]


def clean_word(word: str) -> str:
    return "".join(char for char in word if char.isalnum()).lower().strip()

# collect all timestamped instances of bleep_word in transcript
def query_transcript(bleep_words: list, timestamped_transcript: list) -> list:
    transcript_words = [word for segment in timestamped_transcript for word in segment["words"]]
    detected_bleep_words = []

    for bleep_word in bleep_words:
        for transcript_word in transcript_words:
            if clean_word(transcript_word["text"]) == clean_word(bleep_word):
                detected_bleep_words.append(transcript_word)
    detected_bleep_words = sorted(detected_bleep_words, key=lambda x: x["start"])

    return detected_bleep_words

def replace_bleep(
        og_video_path: str, og_audio_path: str, 
        final_video_path: str, final_audio_path: str, 
        bleep_words: list,
        timestamped_transcript: dict,
    ) -> None:
    # # extract and save audio from original video
    # extract_audio(local_file_path=og_video_path, audio_filepath=og_audio_path)

    # input original audio file for splicing 
    test_sound = AudioSegment.from_mp3(og_audio_path)

    # find bleep words in timestamped transcript
    bleep_word_instances = query_transcript(bleep_words, timestamped_transcript)

    # create test sound with bleeps by splicing in instance 0
    test_clip = test_sound[:1]
    test_sound_clips = [test_clip]

    # loop over instances, thread in clips of bleep
    prev_end_time = 1
    for instance in bleep_word_instances:
        # unpack bleep_word start / end times - converted to microseconds
        start_time = int(instance["start"] * 1000) - 50
        end_time = int(instance["end"] * 1000) + 50

        # collect clip of test starting at previous end time, and leading to start_time of next bleep
        test_clip = test_sound[prev_end_time:start_time]

        # create bleep clip for this instance
        bleep_clip = bleep_first_sec[: (end_time - start_time)]

        # store test and bleep clips
        test_sound_clips.append(test_clip)
        test_sound_clips.append(bleep_clip)

        # update prev_end_time
        prev_end_time = end_time

    # create final clip from test
    test_clip = test_sound[prev_end_time:]
    test_sound_clips.append(test_clip)

    # save bleeped audio
    bleeped_test_clip = sum(test_sound_clips)
    bleeped_test_clip.export(final_audio_path, format="mp3")

    # load in og video, overlay with bleeped audio
    og_video = VideoFileClip(og_video_path)
    bleep_audio = AudioFileClip(final_audio_path)
    new_audioclip = CompositeAudioClip([bleep_audio])
    og_video.audio = new_audioclip
    og_video.write_videofile(
        final_video_path,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
    )
    og_video.close()
    bleep_audio.close()