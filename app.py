import streamlit as st
from pleeb.transcribe import available_models
from pleeb.transcribe import transcribe
from pleeb import main_dir
from pleeb.audio_extractor import extract_audio
from pleeb.create import replace_bleep
# from bleep_that_sht.yt_download import download_video
import tempfile
import base64
import uuid
import io
import os

st.set_page_config(page_title="Pleeb - Meme the Mess")

# Load CSS
def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_file_path = main_dir + "/style/style.css"
load_css(css_file_path)

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64_image("assets/logo_as_of_now.jpg")

st.markdown(f"""
<div class="navbar">
    <div class="nav-left">
        <img src="data:image/jpg;base64,{logo_base64}" alt="Pleeb Logo">
    </div>
    <div class="nav-links">
        <a class="befaft smooth" href="https://github.com/yourusername" target="_blank">GitHub</a>
        <a class="befaft smooth" href="https://www.instagram.com/yourprofile/" target="_blank">Instagram</a>
        <a class="befaft smooth" href="mailto:you@example.com">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)



with st.container(key="main-container"):
    
    st.markdown(f"<h1 class='title'>Pleeb - Meme the Mess</h1>", unsafe_allow_html=True)
    
    with st.container(key="sub-container-1"):
        uploaded_file = st.file_uploader("Choose a video...", type=["mp4"])
        # Optional: Warn for large files
        # if uploaded_file is not None and uploaded_file.size > 50_000_000:
        #     st.warning("Large file detected. Processing may take a while.")

    with st.container(key="sub-container-2"):
        bleep_words = st.text_area(
            label="bleep-word list",
            placeholder="bleep keywords go here separated by commas",
            value="treetz, ice, cream, chocolate, syrup, cookie, hooked, threats, treats",
            key="bleep-words-local"
        )

    with st.container(key="sub-container-3"):
        col1, col2, col3 = st.columns([4, 2, 4])
        with col1:
            model_selection = st.selectbox(
                label="whisper model",
                placeholder="choose whisper model",
                index=1,
                options=available_models
            )
        col4 = st.empty()
        with col4:
            st.write("")
            st.write("")
        with col2:
            trans_button_val = st.button(label="transcribe", type="secondary", key="just-transcribe-local")
        with col3:
            bleep_button_val = st.button(label="transcribe & bleep", type="primary", key="transcribe-bleep-local")


a, col0, b = st.columns([1, 20, 1])
colo1, colo2 = st.columns([3, 3])

def clean_bleep_words(raw_text: str) -> list:
    return [word.strip() for word in raw_text.split(",") if word.strip()]

def button_logic(temporary_video_location: str, model_selection: str, bleep_word_list: list):
    temporary_audio_location = temporary_video_location.replace("mp4", "mp3")
    bleep_video_output = temporary_video_location.replace("original", "bleep")
    bleep_audio_output = bleep_video_output.replace("mp4", "mp3")

    with st.spinner("Processing... Please wait."):
        if trans_button_val:
            extract_audio(temporary_video_location, temporary_audio_location)
            transcript, timestamped_transcript = transcribe(
                local_file_path=temporary_audio_location,
                model=model_selection
            )
            with col0.container():
                st.text_area(
                    value=transcript.strip(),
                    placeholder="transcribe text will be shown here",
                    label="transcribe text",
                )
                st.download_button("Download Transcript", transcript, file_name="transcript.txt")

        if bleep_button_val:
            extract_audio(temporary_video_location, temporary_audio_location)
            transcript, timestamped_transcript = transcribe(
                local_file_path=temporary_audio_location,
                model=model_selection
            )
            with col0.container():
                st.text_area(
                    value=transcript.strip(),
                    placeholder="transcribe text will be shown here",
                    label="transcribe text",
                )
                st.download_button("Download Transcript", transcript, file_name="transcript.txt")
            
            print("BEFORE BLEEP - Temp dir exists:", os.path.exists(tmpdirname))
            print("Contents:", os.listdir(tmpdirname))

            replace_bleep(
                temporary_video_location,
                temporary_audio_location,
                bleep_video_output,
                bleep_audio_output,
                bleep_word_list,
                timestamped_transcript,
            )

            print("AFTER BLEEP - Temp dir exists:", os.path.exists(tmpdirname))
            print("Contents:", os.listdir(tmpdirname))

            with colo2:
                st.caption("bleeped video")
                st.video(bleep_video_output)
                with open(bleep_video_output, "rb") as f:
                    st.download_button("Download Bleeped Video", f, file_name="bleeped_video.mp4")

# Main processing block
default_file = main_dir + "/data/input/pleeb_test_1.mp4"

if uploaded_file is not None:
    byte_file = io.BytesIO(uploaded_file.read())
else:
    filename = open(default_file, "rb")
    byte_file = io.BytesIO(filename.read())

with tempfile.TemporaryDirectory() as tmpdirname:
    temporary_video_location = os.path.join(tmpdirname, "original.mp4")
    with open(temporary_video_location, "wb") as out:
        out.write(byte_file.read())
        with st.container():
            with colo1:
                st.caption("original video")
                st.video(temporary_video_location)

        bleep_words_list = clean_bleep_words(bleep_words)

        if trans_button_val or bleep_button_val:
            button_logic(temporary_video_location, model_selection, bleep_words_list)

st.markdown(
    "### Bleep out words of your choice from an input video.  \n"
    "How it works: \n\n"
    "1.  Provide a YouTube / Shorts URL or upload your own video \n"
    "2.  Choose your desired bleep keywords \n"
    "3.  Choose a model from the Whisper family to transcribe the audio — the larger the model, the more accurate the results, but the more compute power is required. Typically, the smaller `base` model works well. \n"
    "4.  *(Optional)* Press 'Just Transcribe' to examine / download the transcription first (can help pick bleep words) \n"
    "5.  Press 'Transcribe and Bleep' to censor all matching keywords with *beep* sounds \n\n"
    "Note: Whisper models aren’t fine-tuned — you'll sometimes need creative keyword choices for accurate censoring. \n"
    "You do *not* need a GPU to run this app locally. Larger models just take more time. \n"
)
