import streamlit as st
from pleeb.transcribe import available_models, transcribe
from pleeb import main_dir
from pleeb.audio_extractor import extract_audio
from pleeb.create import replace_bleep
from pleeb.create_mtm import bleep_the_mess, meme_the_mess
from assets.pleeb_words import pleeb_words_list

import tempfile
import base64
import io
import os

st.set_page_config(page_title="Pleeb - Meme the Mess")

# Load CSS
def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_file_path = main_dir + "/style/style.css"
load_css(css_file_path)

# Convert image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64_image("assets/logo_as_of_now.jpg")

# Navigation bar
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

main_tab, about_tab = st.tabs(["Pleeb - Meme the Mess", "How Pleeb works"])

with main_tab:
    with st.container(key="main-container"):

        st.markdown(f"<h1 class='title'>Pleeb - Meme the Mess</h1>", unsafe_allow_html=True)

        with st.container(key="sub-container-1"):
            uploaded_file = st.file_uploader("Step 1: Upload a video", type=["mp4"])

        def clean_bleep_words(raw_text: str) -> list:
            return [word.strip() for word in raw_text.split(",") if word.strip()]
        
        with st.container(key="sub-container-2"):
            st.text_area(
                label="Step 2: Enter the words to bleep (separated by commas)",
                placeholder="Example: feel, cool, dude",
                key="bleep-words-local"
            )
            user_enter_words_btn = st.button(
                label="Done",
                type="primary"
            )

            if user_enter_words_btn:
                st.caption("Words to bleep:")
                # st.session_state["bleep-words-local"] = st.session_state.get("bleep-words-local", "")
                st.write(clean_bleep_words(st.session_state.get("bleep-words-local", "")))

        with st.container(key="sub-container-3"):
            col1, col2, col3 = st.columns([4, 2, 4])
            with col1:
                model_selection = st.selectbox(
                    label="Chose a model (Recomended: base)",
                    placeholder="",
                    index=1,
                    options=available_models
                )
            with col2:
                transcribe_only_btn = st.button(label="Transcribe", type="secondary", key="just-transcribe-local")
            with col3:
                transcribe_and_bleep_btn = st.button(label="Transcribe & Bleep", type="primary", key="transcribe-bleep-local")

            st.text("Pleeb: Automatically replace swear words with bleep / random meme sounds")
            col4, col5 = st.columns([3, 3])
            with col4:
                pleeb_mtm_bleep_btn = st.button(label="Transcribe & Auto Bleep", type="primary", key="transcribe-pleeb-bleep-local")
            with col5:
                pleeb_mtm_btn = st.button(label="Transcribe & Meme The Mess", type="primary", key="transcribe-pleeb-mtm-local")

        # Layout for outputs
        a, col0, b = st.columns([1, 20, 1])
        colo1, colo2 = st.columns([3, 3])

        # Main logic handler

        transcribe_only_text_box_bool = False
        def transcribe_only_btn_logic(temporary_video_location: str, model_selection: str):
            temporary_audio_location = temporary_video_location.replace("mp4", "mp3")

            with st.spinner("Processing... Please wait."):
                extract_audio(temporary_video_location, temporary_audio_location)
                transcript, timestamped_transcript = transcribe(
                    local_file_path=temporary_audio_location,
                    model=model_selection
                )

                with col0.container():
                    st.text_area(
                        value=transcript.strip(),
                        placeholder="transcript will be shown here",
                        label="transcribed text",
                    )
                    st.download_button("Download Transcript", transcript, file_name="transcript.txt")


        def transcribe_and_bleep_btn_logic(temporary_video_location: str, model_selection: str, bleep_word_list: list):
            temporary_audio_location = temporary_video_location.replace("mp4", "mp3")
            bleep_video_output = temporary_video_location.replace("original", "bleep")
            bleep_audio_output = bleep_video_output.replace("mp4", "mp3")

            with st.spinner("Processing... Please wait."):

                if not transcribe_only_text_box_bool :
                    extract_audio(temporary_video_location, temporary_audio_location)
                    transcript, timestamped_transcript = transcribe(
                        local_file_path=temporary_audio_location,
                        model=model_selection
                    )

                    with col0.container():
                        st.text_area(
                            value=transcript.strip(),
                            placeholder="transcript will be shown here",
                            label="transcribed text",
                        )
                        st.download_button("Download Transcript", transcript, file_name="transcript.txt")

                replace_bleep(
                    temporary_video_location,
                    temporary_audio_location,
                    bleep_video_output,
                    bleep_audio_output,
                    bleep_word_list,
                    timestamped_transcript,
                )
                with colo1:
                    st.caption("original video")
                    st.video(temporary_video_location)
                with colo2:
                    st.caption("bleeped video")
                    st.video(bleep_video_output)
                with open(bleep_video_output, "rb") as f:
                    st.download_button("Download Bleeped Video", f, file_name="bleeped_video.mp4")

        def pleeb_mtm_btn_logic(temporary_video_location: str, model_selection: str, pleeb_words_list: list):
            temporary_audio_location = temporary_video_location.replace("mp4", "mp3")
            bleep_video_output = temporary_video_location.replace("original", "bleep")
            bleep_audio_output = bleep_video_output.replace("mp4", "mp3")

            with st.spinner("Processing... Please wait."):

                if not transcribe_only_text_box_bool :
                    extract_audio(temporary_video_location, temporary_audio_location)
                    transcript, timestamped_transcript = transcribe(
                        local_file_path=temporary_audio_location,
                        model=model_selection
                    )

                    with col0.container():
                        st.text_area(
                            value=transcript.strip(),
                            placeholder="transcript will be shown here",
                            label="transcribed text",
                        )
                        st.download_button("Download Transcript", transcript, file_name="transcript.txt")
                    
                if pleeb_mtm_bleep_btn:
                    bleep_the_mess(
                        temporary_video_location,
                        temporary_audio_location,
                        bleep_video_output,
                        bleep_audio_output,
                        pleeb_words_list,
                        timestamped_transcript,
                    )
                    with colo1:
                        st.caption("original video")
                        st.video(temporary_video_location)
                    with colo2:
                        st.caption("bleeped video")
                        st.video(bleep_video_output)
                    with open(bleep_video_output, "rb") as f:
                        st.download_button("Download Bleeped Video", f, file_name="bleeped_video.mp4")
                
                if pleeb_mtm_btn:
                    meme_the_mess (
                        temporary_video_location,
                        temporary_audio_location,
                        bleep_video_output,
                        bleep_audio_output,
                        pleeb_words_list,
                        timestamped_transcript,
                    )
                    with colo1:
                        st.caption("original video")
                        st.video(temporary_video_location)
                    with colo2:
                        st.caption("bleeped video")
                        st.video(bleep_video_output)
                    with open(bleep_video_output, "rb") as f:
                        st.download_button("Download Pleebed Video", f, file_name="bleeped_video.mp4")

        if uploaded_file is not None:
            byte_file = io.BytesIO(uploaded_file.read())

            with tempfile.TemporaryDirectory() as tmpdirname:
                temporary_video_location = os.path.join(tmpdirname, "original.mp4")
                with open(temporary_video_location, "wb") as out:
                    out.write(byte_file.read())

                bleep_words_list = clean_bleep_words(st.session_state.get("bleep-words-local", ""))

                if transcribe_only_btn:
                    transcribe_only_btn_logic(temporary_video_location, model_selection)
                    transcribe_only_text_box_bool = True
                if transcribe_and_bleep_btn:
                    transcribe_and_bleep_btn_logic(temporary_video_location, model_selection, bleep_words_list)

                if pleeb_mtm_bleep_btn or pleeb_mtm_btn:
                    pleeb_mtm_btn_logic(temporary_video_location, model_selection, pleeb_words_list)
                    
        else:
            st.info("Upload a video to begin.")


with about_tab:
    with st.container(key="about-container"):
        st.markdown(
            "### How Pleeb works: \n"
            "Step 1. Upload or Drag and drop a video from your computer \n\n"
            "Step 2. Enter the words to bleep (separated by commas) and press 'Done' \n\n"
            "Step 3.  Choose a Machine Learning model to transcribe the audio — (Recommended: base model) The larger the model, the more accurate the results, but the more compute power is required. Typically, the smaller base model works well. \n"
            "### Different Functions (What the buttons do):  \n"
            "1. Transcribe: \n"
            "Transcribe the audio from the uploaded video (video to text) - Can be used to help pick bleep words \n\n"
            "2. Download Transcript: \n"
            "(Appears when you've transcribed) Download the transcribed text if you want \n\n"
            "3. Transcribe and Bleep: \n"
            "Censor all matching keywords that you've entered previously with *bleep* sound \n\n"
            "4. Transcribe and Auto Bleep: \n"
            "Automatically detect all swear words and censor all the swear words with a *bleep* sound \n\n"  
            "5. Transcribe and Meme The Mess: \n"
            "Automatically detect all swear words and censor all the swear words with random *meme* sounds \n\n"
            "6. Download Bleeped Video: \n"
            "(Appears when you've bleeped) Download the video that has been processed based on the function you've selected \n\n"
            "Note: Whisper models aren’t fine-tuned — you'll sometimes need creative keyword choices for accurate censoring. \n"
            "You do *not* need a GPU to run this app locally. Larger models just take more time. \n"
        )