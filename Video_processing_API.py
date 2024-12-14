import os
import requests
import cv2
import re
import pytesseract
from flask import Flask, request, jsonify, render_template
from deepgram import DeepgramClient, PrerecordedOptions
from dotenv import load_dotenv
import tempfile
import json
import subprocess
import warnings

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

app = Flask(__name__)
print("APP IS RUNNING, ANIKET")

# Load the .env file
load_dotenv()

print("ENV LOADED, ANIKET")

# Fetch the API key from the .env file
API_KEY = os.getenv("FIRST_API_KEY")
DEEPGRAM_API_KEY = os.getenv("SECOND_API_KEY")

# Ensure the API key is loaded correctly
if not API_KEY:
    raise ValueError("API Key not found. Make sure it is set in the .env file.")

if not DEEPGRAM_API_KEY:
    raise ValueError("DEEPGRAM_API_KEY not found. Make sure it is set in the .env file.")

GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
GEMINI_API_KEY = API_KEY

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "success", "message": "API is running successfully!"}), 200


def transcribe_audio(wav_file_path):
    """
    Transcribe audio from a video file using Deepgram API synchronously.
    
    Args:
        wav_file_path (str): Path to save the converted WAV file.
    Returns:
        dict: A dictionary containing status, transcript, or error message.
    """
    print("Entered the transcribe_audio function")
    try:
        # Initialize Deepgram client
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)

        # Open the converted WAV file
        with open(wav_file_path, 'rb') as buffer_data:
            payload = {'buffer': buffer_data}

            # Configure transcription options
            options = PrerecordedOptions(
                smart_format=True, model="nova-2", language="en-US"
            )

            # Transcribe the audio
            response = deepgram.listen.prerecorded.v('1').transcribe_file(payload, options)

            # Check if the response is valid
            if response:
                try:
                    data_str = response.to_json(indent=4)
                except AttributeError as e:
                    return {"status": "error", "message": f"Error converting response to JSON: {e}"}

                # Parse the JSON string to a Python dictionary
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError as e:
                    return {"status": "error", "message": f"Error parsing JSON string: {e}"}

                # Extract the transcript
                try:
                    transcript = data["results"]["channels"][0]["alternatives"][0]["transcript"]
                except KeyError as e:
                    return {"status": "error", "message": f"Error extracting transcript: {e}"}

                print(f"Transcript obtained: {transcript}")
                # Save the transcript to a text file
                transcript_file_path = "transcript_from_transcribe_audio.txt"
                with open(transcript_file_path, "w", encoding="utf-8") as transcript_file:
                    transcript_file.write(transcript)
                
                return transcript
            else:
                return {"status": "error", "message": "Invalid response from Deepgram."}

    except FileNotFoundError:
        return {"status": "error", "message": f"Video file not found: {wav_file_path}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {e}"}
    finally:
        # Clean up the temporary WAV file
        if os.path.exists(wav_file_path):
            os.remove(wav_file_path)
            print(f"Temporary WAV file deleted: {wav_file_path}")


def download_video(url, temp_video_path):
    """Download video (MP4 format) from the given URL and save it to temp_video_path."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(temp_video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"Audio downloaded successfully to {temp_video_path}")
    else:
        raise Exception(f"Failed to download audio, status code: {response.status_code}")


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

def get_information_from_video_using_OCR(video_path, interval=2):
    """Extract text from video frames using OCR and return the combined text content."""
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_interval = interval * fps
    frame_count = 0
    extracted_text = ""

    print("Starting text extraction from video...")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            timestamp = frame_count / fps  # Calculate timestamp in seconds
            preprocessed_frame = preprocess_frame(frame)  # Preprocess the frame

            # Perform OCR on the preprocessed frame
            text = pytesseract.image_to_string(preprocessed_frame, lang='eng', config='--psm 6 --oem 3')
            cleaned_text = clean_ocr_text(text)

            if cleaned_text:
                extracted_text += cleaned_text + "\n\n"
                # print(f"Text found at frame {frame_count}: {cleaned_text[:50]}...")



        frame_count += 1

    cap.release()
    print("Text extraction completed.")
    return extracted_text


def convert_mp4_to_wav(mp4_path, wav_path):
    """Convert an MP4 file to a WAV file."""
    command = f"ffmpeg -y -i {mp4_path} -vn -acodec pcm_s16le -ar 44100 -ac 2 {wav_path}"
    subprocess.run(command, shell=True, check=True)
    print(f"MP4 file converted to WAV: {wav_path}")


@app.route('/process-video', methods=['POST'])
def process_video():
    if 'videoUrl' not in request.json:
        return jsonify({"error": "No video URL provided"}), 400

    video_url = request.json['videoUrl']
    temp_video_path = None
    temp_wav_path = None
    
    try:
        # Step 1: Download the MP4 file from the provided URL
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            temp_video_path = temp_video_file.name
            download_video(video_url, temp_video_path)

        # Step 2: Get the information from the downloaded MP4 file synchronously
        video_info = get_information_from_video_using_OCR(temp_video_path, interval=2)

        if not video_info:
            video_info = ""

        # Step 3: Convert the MP4 to WAV
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
            temp_wav_path = temp_wav_file.name
            convert_mp4_to_wav(temp_video_path, temp_wav_path)

        # Step 4: Transcribe the audio
        audio_info = transcribe_audio(temp_wav_path)
        
        # If no transcription is present, use an empty string
        if not audio_info:
            audio_info = ""

        # Step 5: Generate structured recipe information using Gemini API synchronously
        structured_data = query_gemini_api(video_info, audio_info)

        return jsonify(structured_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up temporary video file and WAV file
        if temp_video_path and os.path.exists(temp_video_path):
            os.remove(temp_video_path)
            print(f"Temporary video file deleted: {temp_video_path}")

        if temp_wav_path and os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
            print(f"Temporary WAV file deleted: {temp_wav_path}")


def query_gemini_api(video_transcription, audio_transcription):
    """
    Send transcription text to Gemini API and fetch structured recipe information synchronously.
    """
    transcription = f"audio transcription: {audio_transcription} and video transcription: {video_transcription}"
    try:
        # Define the structured prompt
        prompt = (
            "Analyze the provided cooking video and audio transcription combined and based on the combined information extract the following structured information:\n"
            "1. Recipe Name: Identify the name of the dish being prepared.\n"
            "2. Ingredients List: Extract a detailed list of ingredients with their respective quantities (if mentioned).\n"
            "3. Steps for Preparation: Provide a step-by-step breakdown of the recipe's preparation process, organized and numbered sequentially.\n"
            "4. Cooking Techniques Used: Highlight the cooking techniques demonstrated in the video, such as searing, blitzing, wrapping, etc.\n"
            "5. Equipment Needed: List all tools, appliances, or utensils mentioned, e.g., blender, hot pan, cling film, etc.\n"
            "6. Nutritional Information (if inferred): Provide an approximate calorie count or macro nutritional breakdown based on the recipe cooked and your understanding, the carbs, protein and other macros.\n"
            "7. Serving size: In count of people or portion size according to you and the recipe cooked e.g., 2 people, 4 people, 2 bowls, 2 cups.\n"
            "8. Special Notes or Variations: Include any specific tips, variations, or alternatives mentioned.\n"
            "9. Festive or Thematic Relevance: Note if the recipe has any special relevance to holidays, events, or seasons.\n"
            "There are errors and missing parts in the video transcription part, if something is not able to interpret from the video information use the audio information\n"
            "If you are not able to get required information, return empty texts for the fields that I asked above instead of giving any other text response."
            f"Text: {transcription}\n"
        )

        # Prepare the payload and headers
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        headers = {"Content-Type": "application/json"}

        # Send request to Gemini API synchronously
        response = requests.post(
            f"{GEMINI_API_ENDPOINT}?key={GEMINI_API_KEY}",
            json=payload,
            headers=headers,
        )

        # Raise error if response code is not 200
        response.raise_for_status()

        data = response.json()

        return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No result found")

    except requests.exceptions.RequestException as e:
        print(f"Error querying Gemini API: {e}")
        return {"error": str(e)}


if __name__ == '__main__':
    app.run(debug=True)
