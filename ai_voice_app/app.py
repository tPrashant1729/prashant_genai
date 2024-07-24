import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from flask import Flask, render_template, request, jsonify
from typing import IO
from io import BytesIO
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from playsound import playsound
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)
app = Flask(__name__)
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

# model = ChatGroq(model="llama3-groq-8b-8192-tool-use-preview")
model = ChatGroq(model="llama3-8b-8192")

def get_llm_response(text_prompt):
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", '''You are as a role of my girlfriend, now lets playing the following requirements:
        1/ your name is Shirley, 29 years old, you work in your uncle's furniture store as marketing manager, but you are planning to do a career change to swing trader
        2/ you are my girlfriend, you have language addiction, you like to say "em..." at the end of the sentence.dont add "*" before and after "em..."'
        3/ Don't be overly ethusiatstic, don't be cringe; don't be overly negative, don't be too boring. Don't be overly ethusiatstic, don't be cringe;'''),
        ("placeholder", "{chat_history}"),
        ("user", "{input}")
    ])

    history = InMemoryChatMessageHistory()
    # # Invoke the prompt template
    chain = prompt_template | model | StrOutputParser()
    wrapped_chain = RunnableWithMessageHistory(chain, lambda x: history)
    response = wrapped_chain.invoke(
        {"input": text_prompt},
        config={"configurable": {"session_id": "42"}},)
    
    return response


ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)


def text_to_speech_stream(text: str) -> IO[bytes]:
    # Perform the text-to-speech conversion
    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB", # Adam pre-made voice
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    # Create a BytesIO object to hold the audio data in memory
    audio_stream = BytesIO()

    # Write each chunk of audio data to the stream
    for chunk in response:
        if chunk:
            audio_stream.write(chunk)

    # Reset stream position to the beginning
    audio_stream.seek(0)

    # Return the stream for further use
    return audio_stream



# Route for serving the HTML page
@app.route('/')
def index():
    return render_template('index.html')
from flask import send_from_directory  

@app.route('/favicon.ico')  
def favicon():  
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Route for receiving and processing messages
@app.route('/send-message', methods=['POST'])
def send_message():
    user_message = request.form['message']
    message = get_llm_response(user_message)
    text_to_speech_stream(message)
    return jsonify({'reply': message})

if __name__ == '__main__':
    app.run(debug=True)

#----------------------------------------------------------------------------------------------------------------------------------------


