import aisuite  as ai
from dotenv import load_dotenv
load_dotenv()
client = ai.Client()

models = ["groq:llama3-8b-8192"]

messages = [
    {"role": "system", "content": "Respond in hindi language."},
    {"role": "user", "content": "Tell me a joke on coke."},
]

for model in models:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.75,
        stream=True
    )
    for chunk in response:
        print(chunk.choices[0].delta.content, end="", flush=True)
