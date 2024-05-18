import pyaudio
import asyncio
import websockets
import wave
#from faster_whisper import WhisperModel
#from deep_translator import GoogleTranslator
import speech_recognition as sr
import re
import sys
import json
import urllib
import ffmpeg
import os

import whisperx
import gc

# Define constants
SERVER_HOST = '192.168.0.26'  # Replace with your server's host
SERVER_PORT = 8765  # Replace with your server's port
device = "cuda"
batch_size = 4 # reduce if low on GPU mem
compute_type = "float16"

# save model to local path (optional)
model_dir = "/home/alim/alim_workspace/whisperX/"
#model = whisperx.load_model("large-v3", device, compute_type=compute_type)
model = whisperx.load_model("large-v3", device, compute_type=compute_type, download_root=model_dir)

async def receive_audio(websocket, path):
    print("Client connected.")

    # Extract URL parameters from the path
    url_params = urllib.parse.parse_qs(urllib.parse.urlparse(path).query)
    print(f"URL params: {url_params}")

    ## Access specific parameters
    #if 'src_lang' in url_params:
    #    src_lang = url_params['src_lang'][0]
    #    print(f"source language: {src_lang}")
    #if 'target_lang' in url_params:
    #    target_lang = url_params['target_lang'][0]
    #    print(f"destination language: {target_lang}")

    # Create a file to store the received audio

    try:
        while True:
            audio_file = open("received_audio.mp4", "wb")
            audio_data = await websocket.recv()
            audio_file.write(audio_data)   
            audio_file.close()

            extract_audio('received_audio.mp4', 'received_audio.wav')
            
            ## Google Speech Recognition
            #r = sr.Recognizer()
            #with sr.AudioFile('received_audio.wav') as source:
            #    audio = r.record(source)
            #try:
            #    result = r.recognize_google(audio)
            #    print("Google Speech Recognition thinks you said " + result)
            #    # Send a message back to the client
            #    await websocket.send(result)
            #except sr.UnknownValueError:
            #    print("Google Speech Recognition could not understand audio")
            #except sr.RequestError as e:
            #    print("Could not request results from Google Speech Recognition service; {0}".format(e))

            # Whisper Speech Recognition
            audio = whisperx.load_audio('received_audio.wav')
            result = model.transcribe(audio, batch_size=batch_size)
            result_clean = result["segments"]
            print(result["segments"]) # before alignment
            await websocket.send(json.dumps(result_clean))


    except websockets.exceptions.ConnectionClosedError:
        print("Client connection closed unexpectedly.")

    except Exception as e:
        print(f"Error: {e}")

def extract_audio(mp4_file, output_file):
    try:
        ffmpeg.input(mp4_file).output(output_file, format='wav').run(overwrite_output=True)
        print("Audio extracted successfully.")
    except ffmpeg.Error as e:
        print("Error extracting audio:", e.stderr)


if __name__ == "__main__":
    # Start the WebSocket server
    start_server = websockets.serve(receive_audio, SERVER_HOST, SERVER_PORT)

    print(f"Server started at ws://{SERVER_HOST}:{SERVER_PORT}")

    # Run the server indefinitely
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
