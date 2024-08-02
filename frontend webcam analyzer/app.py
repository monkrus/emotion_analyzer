import os
import time
import logging
import threading
import random
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from PIL import Image
import cv2
import google.generativeai as genai
from io import BytesIO
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configure the API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("API key is not set. Please set the GEMINI_API_KEY environment variable.")

genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-pro')

# Global rate limiter using token bucket
rate_limit_tokens = 5  # Example limit: 5 requests per minute
tokens_lock = threading.Lock()

def replenish_tokens():
    global rate_limit_tokens
    while True:
        time.sleep(12)  # Replenish 1 token every 12 seconds (5 tokens per minute)
        with tokens_lock:
            rate_limit_tokens = min(rate_limit_tokens + 1, 5)

threading.Thread(target=replenish_tokens, daemon=True).start()

def analyze_facial_expression(image):
    prompt = """
    Analyze this image and determine the facial expression of the person.
    Categorize it as one of the following: happy, sad, angry, surprised, neutral, or other.
    If 'other', specify what it might be.
    Also, provide a brief explanation of why you chose that category.
    Finally, estimate the confidence level of your analysis (low, medium, high).
    Based on the detected facial expression, provide advice on how to act to look great, confident, and strong. 
    For example, if the person appears happy, suggest maintaining a positive demeanor. If the person appears sad, suggest offering empathy and support. 
    Tailor the advice to enhance the person's appearance and confidence in situations like interviews, meetings, or social interactions.
    """

    global rate_limit_tokens
    retries = 5
    for i in range(retries):
        with tokens_lock:
            if rate_limit_tokens <= 0:
                delay = 60  # Wait for tokens to replenish
                logging.warning(f"Rate limit tokens exhausted, waiting for {delay} seconds...")
                time.sleep(delay)
            rate_limit_tokens -= 1

        try:
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            with tokens_lock:
                rate_limit_tokens += 1  # Restore token on failure
            if "429" in str(e):
                delay = min(2**i, 30)
                logging.warning(f"Rate limit exceeded, retrying in {delay} seconds...")
                time.sleep(delay + random.uniform(0, 1))  # Add jitter
            elif "500" in str(e):
                delay = min(2**i, 30)
                logging.warning(f"Internal server error, retrying in {delay} seconds...")
                time.sleep(delay + random.uniform(0, 1))  # Add jitter
            else:
                logging.error(f"An error occurred: {e}")
                return None
    return None

def provide_feedback(analysis_result):
    """
    Provide feedback and recommendations based on the analysis result.
    """
    if "happy" in analysis_result:
        return "The person seems happy! Keep the conversation light and positive."
    elif "sad" in analysis_result:
        return "The person might be feeling sad. Consider showing empathy and support."
    elif "angry" in analysis_result:
        return "The person seems upset. It might be best to address any concerns directly."
    elif "surprised" in analysis_result:
        return "The person is surprised! You may have said something unexpected."
    elif "neutral" in analysis_result:
        return "The person appears neutral. Try engaging them with an interesting topic."
    else:
        return "Emotion not clearly identified. Continue being attentive and considerate."

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('analyze_frame')
def handle_analyze_frame(data_image):
    frame_data = data_image.split(",")[1]
    image_data = base64.b64decode(frame_data)
    image = Image.open(BytesIO(image_data))

    logging.info(f"Analyzing frame at {time.time()}:")
    analysis_result = analyze_facial_expression(image)
    if analysis_result:
        feedback = provide_feedback(analysis_result)
        emit('feedback', {'feedback': feedback})
    else:
        emit('feedback', {'feedback': "Error analyzing the frame."})

if __name__ == "__main__":
    socketio.run(app, debug=True)
