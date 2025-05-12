from typing import Tuple
import whisper_timestamped as wts

available_models = ["tiny", "base", "small", "medium", "large"]

def transcribe(local_file_path: str, model: str = "tiny", device: str = "cpu") -> Tuple[str, dict]:
    """
    Transcribe an audio file using Whisper-Timestamped.

    Args:
        local_file_path (str): The path to the local audio file.
        model (str, optional): The model to use for transcription. Defaults to "tiny".
        device (str, optional): The device to use for transcription. Defaults to "cpu".

    Returns:
        Tuple[str, dict]: A tuple containing the transcribed text and a dictionary of metadata.
    """
    assert model in available_models, f"Model {model} is not available. Available models are: {available_models}"
    model = wts.load_model(model, device=device)
    process_output = wts.transcribe(model, local_file_path, verbose=False)
    transcript = process_output["text"]
    timestamped_transcript = process_output["segments"]

    return transcript, timestamped_transcript