from fastapi import FastAPI, File, UploadFile, Form
import os
import openai
import base64
from fastapi.responses import HTMLResponse

app = FastAPI()

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

# Path to your image
# image_path = "/home/dnk131/this_pc/code/prashant_genai/ocrllm/shopping-list-written-in-a-spiral-bound-notebook-S3B4NX.jpg"
image_path = "/home/dnk131/this_pc/code/prashant_genai/ocrllm/stock-photo-honey-do-list-a-handwritten-to-do-list-household-repairs-chores-on-a-clipboard-with-wooden-1639293967.jpg"

# Getting the base64 string
base64_image = encode_image(image_path)

completion = client.chat.completions.create(
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
                        "url": "https://upload.wikimedia.org/wikipedia/commons/d/da/SF_From_Marin_Highlands3.jpg"
                        # "url": f"data:image/jpeg;base64,{base64_image}"
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

from rich.console import Console  
from rich.markdown import Markdown  

# Load your Markdown content  
markdown_content = f'''{completion.choices[0].message.content}'''

console = Console()  
markdown = Markdown(markdown_content)  

# Render the Markdown in the terminal  
console.print(markdown)