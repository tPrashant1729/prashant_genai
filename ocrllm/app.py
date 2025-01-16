import os

# Define the directory structure for the full-fledged app
app_structure = {
    "OCR_App": {
        "backend": {
            "app.py": """
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import os
import openai
import base64

app = FastAPI()

# Set up the OpenAI client
openai.api_base = "https://api.groq.com/openai/v1"
openai.api_key = os.getenv("GROQ_API_KEY")

# Function to encode image to base64
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
        return JSONResponse(content={"error": "No image or URL provided."}, status_code=400)

    # Call the Groq API
    response = openai.Completion.create(
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
                            "url": f"data:image/jpeg;base64,{base64_image}" if image else image_url
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
    with open("frontend/index.html", "r") as f:
        return f.read()

# Mount static files for CSS and JS
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
            """,
        },
        "frontend": {
            "index.html": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/styles.css">
    <title>OCR App</title>
</head>
<body>
    <div class="container">
        <h1>Image to Text Conversion</h1>
        <form id="uploadForm" action="/process-image/" method="post" enctype="multipart/form-data">
            <label for="fileInput">Upload an Image</label>
            <input type="file" id="fileInput" name="image" accept="image/*">
            <p>OR</p>
            <label for="urlInput">Enter Image URL</label>
            <input type="text" id="urlInput" name="image_url" placeholder="https://example.com/image.jpg">
            <button type="submit">Submit</button>
        </form>
        <div id="result">
            <h2>Extracted Text</h2>
            <div id="markdownOutput"></div>
        </div>
    </div>
    <script src="/static/script.js"></script>
</body>
</html>
            """,
            "static": {
                "styles.css": """
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f4f4f9;
}

.container {
    max-width: 800px;
    margin: 50px auto;
    padding: 20px;
    background: #ffffff;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
}

h1 {
    color: #333;
    text-align: center;
}

form {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

input[type="file"],
input[type="text"] {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

button {
    padding: 10px;
    background-color: #007BFF;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background-color: #0056b3;
}

#result {
    margin-top: 20px;
    display: none;
}

#markdownOutput {
    padding: 15px;
    background-color: #f9f9f9;
    border-radius: 4px;
    border: 1px solid #ddd;
    white-space: pre-wrap;
    font-family: monospace;
}
                """,
                "script.js": """
document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    try {
        const response = await fetch("/process-image/", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();
        const outputDiv = document.getElementById("markdownOutput");
        outputDiv.textContent = result.markdown;
        document.getElementById("result").style.display = "block";
    } catch (error) {
        console.error("Error:", error);
    }
});
                """,
            },
        },
    },
}

# Helper function to create directory structure
def create_app_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_app_structure(path, content)
        else:
            with open(path, "w") as file:
                file.write(content)

# Create the directory structure
create_app_structure("./data", app_structure)
