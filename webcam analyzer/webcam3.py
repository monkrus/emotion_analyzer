import os
import google.generativeai as genai
from PIL import Image
import cv2
import time
import logging
import random
import threading

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
            print(response.text)
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


def main():
    # Open the webcam
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        logging.error("Could not open webcam.")
        return

    frame_count = 0
    analysis_interval = 300  # Analyze every 10 seconds (assuming 30 fps)

    logging.info("Press 'q' to quit the program.")

    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                logging.error("Failed to capture frame.")
                break

            frame_count += 1

            # Display the frame
            cv2.imshow('Webcam', frame)

            # Analyze every 10 seconds
            if frame_count % analysis_interval == 0:
                # Convert the frame to PIL Image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)

                logging.info(f"Analyzing frame at {time.time()}:")
                analysis_result = analyze_facial_expression(image)
                if analysis_result:
                    print("\n" + "="*50 + "\n")
                else:
                    break  # Stop processing if an error occurs

            # Check for 'q' key to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Release the webcam and close windows
        video_capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
