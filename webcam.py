import os
import google.generativeai as genai
from PIL import Image
import cv2
import time

# Configure the API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    api_key = input("Please enter your Gemini API key: ")
genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-pro')


def analyze_facial_expression(image):
    prompt = """
    Analyze this image and determine the facial expression of the person.
    Categorize it as one of the following: happy, sad, angry, surprised, neutral, or other.
    If 'other', specify what it might be.
    Also, provide a brief explanation of why you chose that category.
    Finally, estimate the confidence level of your analysis (low, medium, high).
    """

    retries = 5
    for i in range(retries):
        try:
            response = model.generate_content([prompt, image])
            print(response.text)
            return response.text
        except Exception as e:
            if "429" in str(e):
                delay = min(2**i, 30)
                print(f"Rate limit exceeded, retrying in {delay} seconds...")
                time.sleep(delay)
            elif "500" in str(e):
                delay = min(2**i, 30)
                print(f"Internal server error, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"An error occurred: {e}")
                return None
    return None


def main():
    # Open the webcam
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        print("Error: Could not open webcam.")
        return

    frame_count = 0
    analysis_interval = 150  # Analyze every 5 seconds (assuming 30 fps)

    print("Press 'q' to quit the program.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        frame_count += 1

        # Display the frame
        cv2.imshow('Webcam', frame)

        # Analyze every 5 seconds
        if frame_count % analysis_interval == 0:
            # Convert the frame to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)

            print(f"\nAnalyzing frame {frame_count}:")
            analysis_result = analyze_facial_expression(image)
            if analysis_result:
                print("\n" + "="*50 + "\n")
            else:
                break  # Stop processing if an error occurs

        # Check for 'q' key to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close windows
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()