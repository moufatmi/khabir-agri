import edge_tts
import asyncio
import os

async def generate_voice_advice(text: str, output_path: str):
    """
    Generate an MP3 file from text using edge-tts.
    Voice: ar-MA-MounaNeural (Moroccan Female Neural)
    """
    voice = "ar-MA-MounaNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def speak_advice_sync(text: str, output_filename: str = "advice_voice.mp3"):
    """
    Sync wrapper to run the async voice generation.
    Returns the path to the generated file.
    """
    # Create tmp directory if it doesn't exist
    tmp_path = os.path.join(os.getcwd(), "tmp")
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)
        
    full_path = os.path.join(tmp_path, output_filename)
    
    # Run async loop
    asyncio.run(generate_voice_advice(text, full_path))
    
    return full_path
