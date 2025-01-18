
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import os
import openai
import base64
import markdown
from rich.markdown import Markdown

app = FastAPI()


client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)
# Function to encode image to base64
def encode_image(file):
    return base64.b64encode(file).decode('utf-8')

@app.post("/process-image/")
async def process_image(image: UploadFile = File(None), image_url: str = Form(None)):
    if image:
        content = await image.read()
        base64_image = encode_image(content)
        url = f"data:image/jpeg;base64,{base64_image}"
    elif image_url:
        url = image_url
    else:
        return JSONResponse(content={"error": "No image or URL provided."}, status_code=400)

    # Call the Groq API
    response = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": '''Convert the provided image into Markdown format...'''
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": url
                        }
                    }
                ]
            },
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    # Convert Markdown to HTML
    markdown_content = response.choices[0].message.content
    html_content = markdown.markdown(markdown_content,output_format='html',tab_length=1)

    return {"html": html_content}

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("../frontend/index.html", "r") as f:
        return f.read()

# Mount static files for CSS and JS
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")
            