import os
import whisper_timestamped as wts

base_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(base_dir)

model = wts.load_model("tiny", device="cpu")
model = wts.load_model("base", device="cpu")