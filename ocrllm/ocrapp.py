from fastapi import FastAPI, File, UploadFile, Form
import os
import openai
import base64
from fastapi.responses import HTMLResponse

app = FastAPI()
client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

# Function to encode the image
def encode_image(file):
    return base64.b64encode(file).decode('utf-8')

@app.post("/process-image/")
async def process_image(image: UploadFile = File(None), image_url: str = Form(None)):
    if image:
        content = await image.read()
        base64_image = encode_image(content)
    elif image_url:
        base64_image = image_url
    else:
        return {"error": "No image or URL provided."}
    
    response = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": '''Convert the provided image into Markdown format. Ensure that all content from the page is included, such as headers, footers, subtexts, images (with alt text if possible), tables, and any other elements.

                        Requirements:

                        - Output Only Markdown: Return solely the Markdown content without any additional explanations or comments.
                        - No Delimiters: Do not use code fences or delimiters like \`\`\`markdown.
                        - Complete Content: Do not omit any part of the page, including headers, footers, and subtext.'''
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
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
    return {"markdown": response.choices[0].message.content}

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <body>
            <h2>Upload an Image or Enter URL for OCR</h2>
            <form action="/process-image/" method="post" enctype="multipart/form-data">
                <label for="file">Upload Image:</label>
                <input type="file" name="image" id="file">
                <br><br>
                <label for="url">Or Image URL:</label>
                <input type="text" name="image_url" id="url">
                <br><br>
                <button type="submit">Submit</button>
            </form>
        </body>
    </html>
    """