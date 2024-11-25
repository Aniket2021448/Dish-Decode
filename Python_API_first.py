import os
import subprocess
import whisper
import requests
from flask import Flask, request, jsonify, send_file
import tempfile

app = Flask(__name__)

# Gemini API settings
from dotenv import load_dotenv
import requests
# Load the .env file
load_dotenv()

# Fetch the API key from the .env file
API_KEY = os.getenv("FIRST_API_KEY")

# Ensure the API key is loaded correctly
if not API_KEY:
    raise ValueError("API Key not found. Make sure it is set in the .env file.")

GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
GEMINI_API_KEY = API_KEY

# Load Whisper AI model at startup
print("Loading Whisper AI model...")
whisper_model = whisper.load_model("base")  # Choose model size: tiny, base, small, medium, large
print("Whisper AI model loaded successfully.")

@app.route('/process-video', methods=['POST'])
def process_video():
    """
    Flask endpoint to process video:
    1. Extract audio and transcribe using Whisper AI.
    2. Send transcription to Gemini API for recipe information extraction.
    3. Return structured data in the response.
    """
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video']

    try:
        # Save video to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            video_file.save(temp_video_file.name)
            print(f"Video file saved: {temp_video_file.name}")

            # Extract audio and transcribe using Whisper AI
            transcription = transcribe_audio(temp_video_file.name)

            if not transcription:
                return jsonify({"error": "Audio transcription failed"}), 500

            # Generate structured recipe information using Gemini API
            structured_data = query_gemini_api(transcription)

            return jsonify(structured_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up temporary files
        if os.path.exists(temp_video_file.name):
            os.remove(temp_video_file.name)


def transcribe_audio(video_path):
    """
    Extract audio from video file and transcribe using Whisper AI.
    """
    try:
        # Extract audio using ffmpeg
        audio_path = video_path.replace(".mp4", ".wav")
        command = [
            "ffmpeg",
            "-i", video_path,
            "-q:a", "0",
            "-map", "a",
            audio_path
        ]
        subprocess.run(command, check=True)
        print(f"Audio extracted to: {audio_path}")

        # Transcribe audio using Whisper AI
        print("Transcribing audio...")
        result = whisper_model.transcribe(audio_path)

        # Clean up audio file after transcription
        if os.path.exists(audio_path):
            os.remove(audio_path)

        return result.get("text", "").strip()

    except Exception as e:
        print(f"Error in transcription: {e}")
        return None


def query_gemini_api(transcription):
    """
    Send transcription text to Gemini API and fetch structured recipe information.
    """
    try:
        # Define the structured prompt
        prompt = (
            "Analyze the provided cooking video transcription and extract the following structured information:\n"
            "1. Recipe Name: Identify the name of the dish being prepared.\n"
            "2. Ingredients List: Extract a detailed list of ingredients with their respective quantities (if mentioned).\n"
            "3. Steps for Preparation: Provide a step-by-step breakdown of the recipe's preparation process, organized and numbered sequentially.\n"
            "4. Cooking Techniques Used: Highlight the cooking techniques demonstrated in the video, such as searing, blitzing, wrapping, etc.\n"
            "5. Equipment Needed: List all tools, appliances, or utensils mentioned, e.g., blender, hot pan, cling film, etc.\n"
            "6. Nutritional Information (if inferred): Provide an approximate calorie count or nutritional breakdown based on the ingredients used.\n"
            "7. Serving size: In count of people or portion size.\n"
            "8. Special Notes or Variations: Include any specific tips, variations, or alternatives mentioned.\n"
            "9. Festive or Thematic Relevance: Note if the recipe has any special relevance to holidays, events, or seasons.\n"
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

        # Send request to Gemini API
        print("Querying Gemini API...")
        response = requests.post(
            f"{GEMINI_API_ENDPOINT}?key={GEMINI_API_KEY}",
            json=payload,
            headers=headers
        )
        response.raise_for_status()

        # Extract and return the structured data
        data = response.json()
        return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No result found")

    except requests.exceptions.RequestException as e:
        print(f"Error querying Gemini API: {e}")
        return {"error": str(e)}


if __name__ == '__main__':
    app.run(debug=True)
