import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

const App = () => {
  const [emotion, setEmotion] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    const startVideo = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play();
        };
      } catch (err) {
        console.error("Error accessing webcam: ", err);
      }
    };

    startVideo();
  }, []);

  const capture = async () => {
    const context = canvasRef.current.getContext("2d");
    context.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);

    console.log("Captured image from webcam");

    canvasRef.current.toBlob(async (blob) => {
      const formData = new FormData();
      formData.append("file", blob, "screenshot.jpg");

      try {
        const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/analyze`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        console.log("Response from backend:", response.data);
        setEmotion(response.data);
      } catch (error) {
        console.error("Error analyzing the image: ", error);
      }
    });
  };

  return (
    <div>
      <h1>Face Expression Analyzer</h1>
      <video ref={videoRef} style={{ display: "block" }}></video>
      <canvas ref={canvasRef} width="640" height="480" style={{ display: "none" }}></canvas>
      <button onClick={capture}>Capture & Analyze</button>
      {emotion && (
        <div>
          <h2>Detected Emotions</h2>
          <pre>{JSON.stringify(emotion, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default App;
