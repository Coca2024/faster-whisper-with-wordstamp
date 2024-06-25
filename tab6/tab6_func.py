import asyncio
import random
import os
import edge_tts
from edge_tts import VoicesManager
import tempfile
import gradio as gr

async def amain(text_for_reading, voice_choice) -> str:
    # Create a temporary output file path
    if text_for_reading==None or voice_choice==None:
        return None
    base_name = os.path.splitext(os.path.basename(text_for_reading))[0]
    temp_dir = tempfile.gettempdir()
    output_file_name = f"{base_name}.mp3"
    OUTPUT_FILE = os.path.join(temp_dir, output_file_name)

    # Read the input text
    with open(text_for_reading, 'r', encoding='utf-8') as file:
        TEXT = file.read()


    # Get available voices
    voices = await VoicesManager.create()

    # Choose the appropriate gender
    Gender = "Male" if voice_choice == "男性" else "Female"
    voice = voices.find(Gender=Gender, Language="ja")
    
    # Randomly select a voice from the available voices
    selected_voice = random.choice(voice)["Name"]

    # Perform text-to-speech
    communicate = edge_tts.Communicate(TEXT, selected_voice)
    await communicate.save(OUTPUT_FILE)
    
    return OUTPUT_FILE

def tts(text, voice):
    # Run the asyncio event loop to execute the async function
    output_file = asyncio.run(amain(text, voice))
    return output_file, output_file
