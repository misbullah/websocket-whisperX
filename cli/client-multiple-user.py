import asyncio
import websockets
import json

async def send_audio(websocket, filename):
    # Open the WAV file and read its content
    with open(filename, 'rb') as f:
        audio_data = f.read()

    # Send the audio data to the server
    await websocket.send(audio_data)
    print("Audio file sent successfully!")

async def receive_and_process_message(websocket):
    message = await websocket.recv()
    result_clean = json.loads(message)
    # Process the received message (result_clean) here
    print("Received message from server:", result_clean)

async def connect_and_send(uri, filename):
    async with websockets.connect(uri) as websocket:
        await send_audio(websocket, filename)

    # Receive and process the message from the server
        await receive_and_process_message(websocket)

async def main():
    uri = "ws://192.168.0.11:8765"
    filenames = ["Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav", "Alim-Recording-EN-03062024.wav"]

    # Create tasks for each client connection
    tasks = [connect_and_send(uri, filename) for filename in filenames]

    # Run tasks concurrently
    await asyncio.gather(*tasks)

asyncio.run(main())

