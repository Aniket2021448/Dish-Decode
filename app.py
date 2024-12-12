import os
import whisper
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from deepgram import DeepgramClient, PrerecordedOptions
import tempfile
import json
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi


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


def download_audio(url, temp_audio_path):
    """Download audio (WAV format) from the given URL and save it to temp_audio_path."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(temp_audio_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"Audio downloaded successfully to {temp_audio_path}")
    else:
        raise Exception(f"Failed to download audio, status code: {response.status_code}")

@app.route('/process-audio', methods=['POST'])
def process_audio():
    if 'audioUrl' not in request.json:
        return jsonify({"error": "No audio URL provided"}), 400

    audio_url = request.json['audioUrl']
    temp_audio_path = None

    try:
        # Step 1: Download the WAV file from the provided URL
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            temp_audio_path = temp_audio_file.name
            download_audio(audio_url, temp_audio_path)

        # Step 2: Transcribe the downloaded WAV file synchronously
        transcription = transcribe_audio(temp_audio_path)

        if not transcription:
            return jsonify({"error": "Audio transcription failed"}), 500

        # Step 3: Generate structured recipe information using Gemini API synchronously
        structured_data = query_gemini_api(transcription)

        return jsonify(structured_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up temporary audio file
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            print(f"Temporary audio file deleted: {temp_audio_path}")



import logging
logging.basicConfig(level=logging.DEBUG)

from urllib.parse import urlparse, parse_qs

def extract_video_id(youtube_url):
    """
    Extracts the video ID from a YouTube URL.
    """
    try:
        parsed_url = urlparse(youtube_url)
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get('v', [None])[0]
        return video_id
    except Exception as e:
        print(f"Error extracting video ID: {e}")
        return None


@app.route('/process-youtube', methods=['POST'])
def process_youtube():
    youtube_url = request.json.get('youtube_url')
    
    if not youtube_url:
        return jsonify({"error": "No YouTube URL provided"}), 400

    try:
        # Extract the video ID from the YouTube URL
        video_id = extract_video_id(youtube_url)
        
        logging.debug(f"Processing video ID: {video_id}")
        
        try:
            # Fetch transcript
            # transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript_data = transcript_list.find_generated_transcript(['en'])

            transcript = transcript_data.fetch()[0]
            
        except Exception as e:
            logging.error(f"Error fetching transcript for {video_id}: {e}")
            return jsonify({"error": f"Could not retrieve transcript for video {video_id}: {str(e)}"}), 500

        # Concatenate transcript
        # transcript = " ".join([segment['text'] for segment in transcript_data])
        logging.debug(f"Transcript: {transcript}")

        # Send to Gemini API
        structured_data = query_gemini_api(transcript)

        # Return structured data
        return jsonify(structured_data)

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": str(e)}), 500



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
                # print("Request successful! Processing response.")

                # Convert response to JSON string
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
                # Step: Save the transcript to a text file
                transcript_file_path = "transcript_from_transcribe_audio.txt"
                with open(transcript_file_path, "w", encoding="utf-8") as transcript_file:
                    transcript_file.write(transcript)
                # print(f"Transcript saved to file: {transcript_file_path}")
                
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


def query_gemini_api(transcription):
    """
    Send transcription text to Gemini API and fetch structured recipe information synchronously.
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



