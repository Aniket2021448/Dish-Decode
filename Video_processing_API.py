import os
import requests
import cv2
import re
import pytesseract
from flask import Flask, request, jsonify
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv


# Flask app
app = Flask(__name__)

# Configure Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure Google Gemini API key
configure(api_key='YOUR_GEMINI_API_KEY')
gemini_model = GenerativeModel('gemini-pro')

# Directory to save downloaded videos
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_video(cloudinary_url):
    """Download video from Cloudinary link and return the local file path."""
    response = requests.get(cloudinary_url, stream=True)
    if response.status_code == 200:
        video_path = os.path.join(DOWNLOAD_DIR, 'downloaded_video.mp4')
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"Video downloaded successfully to {video_path}")
        return video_path
    else:
        raise Exception(f"Failed to download video: {response.status_code}")

def preprocess_frame(frame):
    """Preprocess the frame for better OCR accuracy."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    denoised = cv2.medianBlur(gray, 3)
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return thresh

def clean_ocr_text(text):
    """Clean the OCR output by removing noise and unwanted characters."""
    cleaned_text = re.sub(r'[^A-Za-z0-9\s,.!?-]', '', text)
    cleaned_text = '\n'.join([line.strip() for line in cleaned_text.splitlines() if len(line.strip()) > 2])
    return cleaned_text

def extract_text_from_video(video_path, interval=1):
    """Extract text from video and return the text content."""
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_interval = interval * fps
    frame_count = 0
    extracted_text = ""

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            preprocessed_frame = preprocess_frame(frame)
            text = pytesseract.image_to_string(preprocessed_frame, lang='eng', config='--psm 6 --oem 3')
            cleaned_text = clean_ocr_text(text)
            if cleaned_text:
                extracted_text += cleaned_text + "\n\n"
                # Save the first frame with text
                if frame_count == 0:
                    cv2.imwrite("first_frame.png", frame)

        frame_count += 1

    cap.release()
    return extracted_text

def send_to_gemini(text):
    """Send extracted text to Gemini API and return structured information."""
    prompt = f"Please structure the following extracted recipe information:\n\n{text}"
    response = gemini_model.generate_content(prompt)
    return response.text

@app.route('/process-video', methods=['POST'])
def process_video():
    """Endpoint to process video from Cloudinary link."""
    try:
        # Get Cloudinary link from request
        data = request.json
        cloudinary_url = data.get('cloudinary_url')
        if not cloudinary_url:
            return jsonify({"error": "No Cloudinary URL provided"}), 400

        # Download video
        video_path = download_video(cloudinary_url)

        # Extract text from video
        extracted_text = extract_text_from_video(video_path)
        if not extracted_text:
            return jsonify({"error": "No text found in the video"}), 400

        # Send extracted text to Gemini API
        structured_info = send_to_gemini(extracted_text)

        # Return structured information
        return jsonify({"structured_info": structured_info})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
