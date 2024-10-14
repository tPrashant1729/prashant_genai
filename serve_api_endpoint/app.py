from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()
groq_api_key = os.environ.get('GROQ_API_KEY')
client = Groq(api_key=groq_api_key)

# Initialize FastAPI client
app = FastAPI()

# Create class with pydantic BaseModel
class TranslationRequest(BaseModel):
    input_str: str


def translate_text(input_str):
    completion = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {
            "role": "system",
            "content": "You are an expert translator who translates text from english to french and only return translated text",
        },
        {"role": "user", "content": input_str}
    ],
    )
    return completion.choices[0].message.content


@app.post("/translate/")  # This line decorates 'translate' as a POST endpoint
async def translate(request: TranslationRequest):
    try:
        # Call your translation function
        translated_text = translate_text(request.input_str)
        return {"translated_text": translated_text}
    except Exception as e:
        # Handle exceptions or errors during translation
        raise HTTPException(status_code=500, detail=str(e))