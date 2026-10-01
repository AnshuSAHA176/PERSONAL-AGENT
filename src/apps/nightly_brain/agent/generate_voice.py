import base64
import os
from pathlib import Path
from dotenv import load_dotenv
from speechify import Speechify
from ..models import VoiceBriefing

load_dotenv()
def generate_speech(
    text: str,
    
    voice_id: str = "geffen_32",
    model: str = "simba-3.2",
) -> str:
    """Generate speech from text and save it as an MP3 file."""
    try:
            token = os.getenv("SPEECHIFY_API_KEY")
            if not token:
                raise ValueError("SPEECHIFY_API_KEY is not set")

            client = Speechify(token=token)

            response = client.audio.speech(
                input=text,
                voice_id=voice_id,
                model=model,
                audio_format="mp3",
            )

            return  base64.b64decode(response.audio_data)
            


    except Exception as e:
         return "somthing wrong"
            
    


# Example

