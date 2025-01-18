# app.py

from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import uuid
from PIL import Image
import io
import websocket
import json
import urllib.request
import urllib.parse

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    print(f"Sending data: {data}")  # Log the data being sent
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    try:
        response = urllib.request.urlopen(req).read()
        print(f"Response: {response}")  # Log the response
        return json.loads(response)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")  # Log the HTTP error
        print(f"Response: {e.read()}")  # Log the response body
        raise

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    current_node = ""
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['prompt_id'] == prompt_id:
                    if data['node'] is None:
                        break  # Execution is done
                    else:
                        current_node = data['node']
                        print(current_node)
        else:
            if current_node == 'save_image_websocket_node':
                images_output = output_images.get(current_node, [])
                images_output.append(out[8:])
                output_images[current_node] = images_output

    return output_images

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = f"{uuid.uuid4()}.png"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Process the image

        with open('/home/dnk131/Desktop/fast_final.json', 'r') as file:
            prompt = json.load(file)
        # Set the text prompt for our positive CLIPTextEncode
        prompt["10"]["inputs"]["image"] = "./uploads/" + filename
        print("filepath",prompt["10"]["inputs"]["image"])

        # Set the seed for our KSampler node
        prompt["3"]["inputs"]["seed"] = 5
        ws = websocket.WebSocket()
        ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
        images = get_images(ws, prompt)
        for node_id in images:
            for image_data in images[node_id]:
                image = Image.open(io.BytesIO(image_data))
                processed_img = image
                processed_filename = f"{uuid.uuid4()}.png"
                processed_file_path = os.path.join(PROCESSED_FOLDER, processed_filename)
                processed_img.save(processed_file_path)

        return jsonify({'processed_image_url': f"/processed/{processed_filename}"}), 200

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)