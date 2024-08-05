# Emotion_analyzer is a collection of various approaches to recognize human emotions
`pip install google-generativeai pillow opencv-python time`
 
**Analyze the emotions of the person based on the image or video** 
**(image and video analyzer).**

1. Upload image or video to colab

**Analyze the emotions of the person in live webcam session.**
**(webcam analyzer)**

 1. Emotion analyzer.ipynb is for image/video analysis
 2. webcam1.py is initial approach to analyze real-time emotions during the live webcam session
 3. webcam3.py is the most succesful version as of right now
 4. webcam4.py is the playground/testing arena


**An example of basic fastapi react setup, no face analisys here!**
(fastapi react basic setup)

- BACKEND (FastAPI)
1. Install FastAPI and Uvicorn
`pip install fastapi uvicorn`
2. Add CORS middleware
3. Run the FastAPI Server
`uvicorn main:app --reload`
4. Test the endpoint by opening http://127.0.0.1:8000/message in your browser. 

- FRONTEND (React)
1. Create React App
`npx create-react-app my-react-app`
2. Install Axios
`npm install axios`
3. Create a Component to Fetch Data (MessageComponent.js)
4. Update App.js
5. Start the React App
`npm start`
6. Open a browser and navigate to http://localhost:3000. 

**An example of fastapi react setup using Micorsoft Azure Face resource**
`pip install fastapi uvicorn aiohttp`
Follow the backend and frontend steps in the previous example.

