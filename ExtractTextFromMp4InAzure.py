import os
import time
import gc
import wave
import contextlib
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
import azure.cognitiveservices.speech as speechsdk
from moviepy import VideoFileClip

def split_wav_by_time(wav_path, chunk_duration_sec=15):
    chunks = []
    with contextlib.closing(wave.open(wav_path, 'rb')) as wf:
        frame_rate = wf.getframerate()
        n_frames = wf.getnframes()
        n_channels = wf.getnchannels()
        samp_width = wf.getsampwidth()

        total_duration = n_frames / frame_rate
        total_chunks = int(total_duration // chunk_duration_sec) + 1

        for i in range(total_chunks):
            start_frame = int(i * chunk_duration_sec * frame_rate)
            end_frame = int(min((i+1) * chunk_duration_sec * frame_rate, n_frames))
            chunk_frames = end_frame - start_frame

            chunk_file = f"chunk_{i}.wav"
            with wave.open(chunk_file, 'wb') as chunk_wf:
                chunk_wf.setnchannels(n_channels)
                chunk_wf.setsampwidth(samp_width)
                chunk_wf.setframerate(frame_rate)

                wf.setpos(start_frame)
                frames = wf.readframes(chunk_frames)
                chunk_wf.writeframes(frames)

            chunks.append(chunk_file)
    return chunks

def extract_text_from_mp4(
    connection_string: str,
    container_name: str,
    blob_name: str,
    speech_service_endpoint: str,
    speech_service_api_key: str,
    chunk_duration_sec: int = 15
) -> str:
    # Download video file
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    local_video = "temp_downloaded.mp4"
    try:
        with open(local_video, "wb") as f:
            f.write(blob_client.download_blob().readall())
    except ResourceNotFoundError:
        raise FileNotFoundError(f"Blob '{blob_name}' not found in container '{container_name}'.")

    # Extract full audio
    audio_file = "temp_audio.wav"
    with VideoFileClip(local_video) as video:
        audio = video.audio
        audio.write_audiofile(audio_file, codec='pcm_s16le', fps=16000)

    # Split audio into chunks
    audio_chunks = split_wav_by_time(audio_file, chunk_duration_sec=chunk_duration_sec)

    all_texts = []
    speech_config = speechsdk.SpeechConfig(subscription=speech_service_api_key, endpoint=speech_service_endpoint)

    # Recognize each chunk
    for chunk_file in audio_chunks:
        audio_config = speechsdk.AudioConfig(filename=chunk_file)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        result = recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            all_texts.append(result.text)
        else:
            all_texts.append("")

        # Release resources and wait before deleting file
        del recognizer
        gc.collect()
        time.sleep(0.2)
        os.remove(chunk_file)

    # Cleanup
    os.remove(local_video)
    os.remove(audio_file)

    return "\n".join(all_texts)
