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
from datetime import datetime
import psutil

import whisperx
import gc

# Define constants
SERVER_HOST = '192.168.0.11'  # Replace with your server's host
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

    ## Extract URL parameters from the path
    #url_params = urllib.parse.parse_qs(urllib.parse.urlparse(path).query)
    #print(f"URL params: {url_params}")

    # Create a file to store the received audio

    try:
        while True:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=0)

            # Get memory usage
            mem = psutil.virtual_memory()
            mem_percent = mem.percent

            print(f"cpu_percent: {cpu_percent}, mem_percent: {mem_percent}")

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"received_audio_{timestamp}.wav"
            

            with open(filename, "wb") as audio_file:
                audio_data = await websocket.recv()

                if not audio_data:
                    break
                
                audio_file.write(audio_data)

            audio_file.close()

            # Whisper Speech Recognition
            audio = whisperx.load_audio(filename)
            result = model.transcribe(audio, batch_size=batch_size)
            result_clean = result["segments"]
            print(result["segments"]) # before alignment
            await websocket.send(json.dumps(result_clean))


    except websockets.exceptions.ConnectionClosedError:
        print("Client connection closed unexpectedly.")

if __name__ == "__main__":
    # Start the WebSocket server
    start_server = websockets.serve(receive_audio, SERVER_HOST, SERVER_PORT)

    print(f"Server started at ws://{SERVER_HOST}:{SERVER_PORT}")

    # Run the server indefinitely
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
