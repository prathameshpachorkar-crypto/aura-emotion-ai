from flask import Flask, render_template, request, jsonify, Response
import emotion_detection.detect_emotion as ed
from chatbot.gemini_chat import generate_emotion_response

app = Flask(__name__)

@app.route('/')
def index():
    # Serves the main frontend page
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    data = request.json
    image_data = data.get("image")
    if not image_data:
        return jsonify({"error": "No image data"}), 400
        
    emotion = ed.process_image_data(image_data)
    return jsonify({"emotion": emotion})

@app.route('/get_current_emotion', methods=['GET'])
def get_current_emotion():
    # Frontend will poll this endpoint to update the UI label
    return jsonify({"emotion": ed.LATEST_EMOTION})

@app.route('/toggle_camera', methods=['POST'])
def toggle_camera():
    data = request.json
    state = data.get("state", True)
    ed.set_camera_state(state)
    return jsonify({"status": "success", "camera_active": state})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message")
    
    # Grab the globally detected emotion
    current_emotion = ed.LATEST_EMOTION
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
        
    # Get response adapted to current emotion
    bot_reply = generate_emotion_response(user_message, current_emotion)
    
    return jsonify({
        "response": bot_reply,
        "emotion_used": current_emotion
    })

if __name__ == '__main__':
    # Running locally on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)