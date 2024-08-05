from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import requests

app = FastAPI()

# Add CORS middleware to allow requests from the React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # This should match the origin of your React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        subscription_key = os.getenv("AZURE_FACE_KEY")
        endpoint = os.getenv("AZURE_FACE_ENDPOINT")

        image = await file.read()

        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Content-Type': 'application/octet-stream'
        }
        params = {
            'returnFaceId': 'true',
            'returnFaceAttributes': 'emotion'
        }
        response = requests.post(
            f"{endpoint}/face/v1.0/detect", params=params, headers=headers, data=image
        )

        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return {"error": str(http_err)}, 500
    except Exception as err:
        print(f"Other error occurred: {err}")
        return {"error": str(err)}, 500
