from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
import json
import uuid
import urllib.request
import urllib.parse
import threading
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app)


app = Flask(__name__)

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

# Load the JSON file at startup
with open('./workflow_api.json', 'r') as file:
    prompt = json.load(file)

# Function to handle WebSocket communication
def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break  # Execution is done
        else:
            continue  # previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        if 'images' in node_output:
            images_output = []
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
            output_images[node_id] = images_output

    return output_images

# Queue a prompt on the ComfyUI server
def queue_prompt(prompt_data):
    p = {"prompt": prompt_data, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
        return json.loads(response.read())

@app.route('/')
def index():
    return render_template('index.html')


# Dictionary to keep track of active threads and flags
generation_threads = {}
generation_active_flags = {}

@app.route('/generate', methods=['POST'])
def generate_image():
    user_input = request.json
    new_text_pos = user_input.get('positivePrompt', 'default prompt')
    client_id = user_input.get('clientId')

    # Function to simulate image generation in a thread
    def image_generation():
        if not generation_active_flags.get(client_id, False):
            return  # If canceled before generation started

        # Simulate a long-running image generation process (e.g., calling ComfyUI)
        for i in range(60):
            if not generation_active_flags.get(client_id, False):
                return  # Exit if generation was canceled
            time.sleep(60)  # Simulate time-consuming image generation

        if generation_active_flags.get(client_id, False):
            # Simulate success, returning base64 encoded image (replace with real logic)
            del generation_threads[client_id]
            del generation_active_flags[client_id]
            return jsonify({'image': 'base64-image-data'})
        else:
            return jsonify({'message': 'Image generation was canceled'}), 400

    # Start the generation process in a new thread
    generation_active_flags[client_id] = True
    generation_threads[client_id] = threading.Thread(target=image_generation)
    generation_threads[client_id].start()

    return jsonify({'message': 'Image generation started'})

@app.route('/cancel', methods=['POST'])
def cancel_image_generation():
    user_input = request.json
    client_id = user_input.get('clientId')

    if client_id in generation_active_flags and generation_active_flags[client_id]:
        generation_active_flags[client_id] = False  # Flag the thread to stop
        return jsonify({'message': 'Image generation canceled'})
    else:
        return jsonify({'message': 'No generation found for this clientId'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
