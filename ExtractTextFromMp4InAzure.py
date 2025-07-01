import os
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
import azure.cognitiveservices.speech as speechsdk
from moviepy import VideoFileClip
import threading

# Function to extract text from an MP4 file stored in Azure Blob Storage
def extract_text_from_mp4(
    connection_string: str,
    container_name: str,
    blob_name: str,
    speech_service_endpoint: str,
    speech_service_api_key: str
) -> str:
    # Download MP4 file from Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    local_file_name = "temp_downloaded.mp4"
    try:
        with open(local_file_name, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
    except ResourceNotFoundError:
        raise FileNotFoundError(f"Blob '{blob_name}' not found in container '{container_name}'.")

    # Extract audio from MP4 using moviepy
    audio_file = "temp_audio.wav"
    with VideoFileClip(local_file_name) as video:
        audio = video.audio
        audio.write_audiofile(audio_file, codec='pcm_s16le')

    print("Done writing audio file")

    # Use Azure Form Recognizer (or Speech-to-Text) to extract text from audio
    # Here, we use Azure Speech SDK for speech-to-text
    print("Starting speech recognition...")
    speech_config = speechsdk.SpeechConfig(subscription=speech_service_api_key, endpoint=speech_service_endpoint)
    audio_input = speechsdk.AudioConfig(filename=audio_file)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    all_results = []

    def handle_result(evt):
        if evt.result.text:
            all_results.append(evt.result.text)

    speech_recognizer.recognized.connect(handle_result)
    speech_recognizer.session_stopped.connect(lambda evt: stop_continuous_recognition.set())
    speech_recognizer.canceled.connect(lambda evt: stop_continuous_recognition.set())

    stop_continuous_recognition = threading.Event()

    speech_recognizer.start_continuous_recognition()
    stop_continuous_recognition.wait()
    speech_recognizer.stop_continuous_recognition()

    text = " \n".join(all_results)
    # ...existing code...

    # Clean up temp files
    os.remove(local_file_name)
    os.remove(audio_file)

    return text