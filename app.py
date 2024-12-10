# # import os
# # import subprocess
# # import whisper
# # import requests
# # from flask import Flask, request, jsonify, send_file, render_template
# # import tempfile

# # app = Flask(__name__)

# # # Gemini API settings
# # from dotenv import load_dotenv
# # import requests
# # # Load the .env file
# # load_dotenv()

# # # Fetch the API key from the .env file
# # API_KEY = os.getenv("FIRST_API_KEY")

# # # Ensure the API key is loaded correctly
# # if not API_KEY:
# #     raise ValueError("API Key not found. Make sure it is set in the .env file.")

# # GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
# # GEMINI_API_KEY = API_KEY

# # # Load Whisper AI model at startup
# # print("Loading Whisper AI model...")
# # whisper_model = whisper.load_model("base")  # Choose model size: tiny, base, small, medium, large
# # print("Whisper AI model loaded successfully.")


# # # Define the "/" endpoint for health check
# # @app.route("/", methods=["GET"])
# # def health_check():
# #     return jsonify({"status": "success", "message": "API is running successfully!"}), 200

# # @app.route("/mbsa")
# # def mbsa():
# #     return render_template("mbsa.html")

# # @app.route('/process-video', methods=['POST'])
# # def process_video():
# #     """
# #     Flask endpoint to process video:
# #     1. Extract audio and transcribe using Whisper AI.
# #     2. Send transcription to Gemini API for recipe information extraction.
# #     3. Return structured data in the response.
# #     """
# #     if 'video' not in request.files:
# #         return jsonify({"error": "No video file provided"}), 400

# #     video_file = request.files['video']

# #     try:
# #         # Save video to a temporary file
# #         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
# #             video_file.save(temp_video_file.name)
# #             print(f"Video file saved: {temp_video_file.name}")

# #             # Extract audio and transcribe using Whisper AI
# #             transcription = transcribe_audio(temp_video_file.name)

# #             if not transcription:
# #                 return jsonify({"error": "Audio transcription failed"}), 500

# #             # Generate structured recipe information using Gemini API
# #             structured_data = query_gemini_api(transcription)

# #             return jsonify(structured_data)

# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500

# #     finally:
# #         # Clean up temporary files
# #         if os.path.exists(temp_video_file.name):
# #             os.remove(temp_video_file.name)


# # def transcribe_audio(video_path):
# #     """
# #     Extract audio from video file and transcribe using Whisper AI.
# #     """
# #     try:
# #         # Extract audio using ffmpeg
# #         audio_path = video_path.replace(".mp4", ".wav")
# #         command = [
# #             "ffmpeg",
# #             "-i", video_path,
# #             "-q:a", "0",
# #             "-map", "a",
# #             audio_path
# #         ]
# #         subprocess.run(command, check=True)
# #         print(f"Audio extracted to: {audio_path}")

# #         # Transcribe audio using Whisper AI
# #         print("Transcribing audio...")
# #         result = whisper_model.transcribe(audio_path)

# #         # Clean up audio file after transcription
# #         if os.path.exists(audio_path):
# #             os.remove(audio_path)

# #         return result.get("text", "").strip()

# #     except Exception as e:
# #         print(f"Error in transcription: {e}")
# #         return None


# # def query_gemini_api(transcription):
# #     """
# #     Send transcription text to Gemini API and fetch structured recipe information.
# #     """
# #     try:
# #         # Define the structured prompt
# #         prompt = (
# #             "Analyze the provided cooking video transcription and extract the following structured information:\n"
# #             "1. Recipe Name: Identify the name of the dish being prepared.\n"
# #             "2. Ingredients List: Extract a detailed list of ingredients with their respective quantities (if mentioned).\n"
# #             "3. Steps for Preparation: Provide a step-by-step breakdown of the recipe's preparation process, organized and numbered sequentially.\n"
# #             "4. Cooking Techniques Used: Highlight the cooking techniques demonstrated in the video, such as searing, blitzing, wrapping, etc.\n"
# #             "5. Equipment Needed: List all tools, appliances, or utensils mentioned, e.g., blender, hot pan, cling film, etc.\n"
# #             "6. Nutritional Information (if inferred): Provide an approximate calorie count or nutritional breakdown based on the ingredients used.\n"
# #             "7. Serving size: In count of people or portion size.\n"
# #             "8. Special Notes or Variations: Include any specific tips, variations, or alternatives mentioned.\n"
# #             "9. Festive or Thematic Relevance: Note if the recipe has any special relevance to holidays, events, or seasons.\n"
# #             f"Text: {transcription}\n"
# #         )

# #         # Prepare the payload and headers
# #         payload = {
# #             "contents": [
# #                 {
# #                     "parts": [
# #                         {"text": prompt}
# #                     ]
# #                 }
# #             ]
# #         }
# #         headers = {"Content-Type": "application/json"}

# #         # Send request to Gemini API
# #         print("Querying Gemini API...")
# #         response = requests.post(
# #             f"{GEMINI_API_ENDPOINT}?key={GEMINI_API_KEY}",
# #             json=payload,
# #             headers=headers
# #         )
# #         response.raise_for_status()

# #         # Extract and return the structured data
# #         data = response.json()
# #         return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No result found")

# #     except requests.exceptions.RequestException as e:
# #         print(f"Error querying Gemini API: {e}")
# #         return {"error": str(e)}


# # if __name__ == '__main__':
# #     app.run(debug=True)



# ## above code is working fine, on local
# ## Below code is taken frmo HUggging face ,


# # Above code is without polling and sleep

# import os
# import subprocess
# import whisper
# import requests
# from flask import Flask, request, jsonify, send_file, render_template
# import tempfile

# app = Flask(__name__)

# # Gemini API settings
# from dotenv import load_dotenv
# import requests
# # Load the .env file
# load_dotenv()

# # Fetch the API key from the .env file
# API_KEY = os.getenv("FIRST_API_KEY")

# # Ensure the API key is loaded correctly
# if not API_KEY:
#     raise ValueError("API Key not found. Make sure it is set in the .env file.")

# GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
# GEMINI_API_KEY = API_KEY

# # Load Whisper AI model at startup
# print("Loading Whisper AI model...")
# whisper_model = whisper.load_model("base")  # Choose model size: tiny, base, small, medium, large
# print("Whisper AI model loaded successfully.")


# # Define the "/" endpoint for health check
# @app.route("/", methods=["GET"])
# def health_check():
#     return jsonify({"status": "success", "message": "API is running successfully!"}), 200

# @app.route("/mbsa")
# def mbsa():
#     return render_template("mbsa.html")

# @app.route('/process-video', methods=['POST'])
# def process_video():
#     """
#     Flask endpoint to process video:
#     1. Extract audio and transcribe using Whisper AI.
#     2. Send transcription to Gemini API for recipe information extraction.
#     3. Return structured data in the response.
#     """
#     if 'video' not in request.files:
#         return jsonify({"error": "No video file provided"}), 400

#     video_file = request.files['video']

#     try:
#         # Save video to a temporary file
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
#             video_file.save(temp_video_file.name)
#             print(f"Video file saved: {temp_video_file.name}")
            
#             # Extract audio and transcribe using Whisper AI
#             transcription = transcribe_audio(temp_video_file.name)

#             if not transcription:
#                 return jsonify({"error": "Audio transcription failed"}), 500

#             # Generate structured recipe information using Gemini API
#             structured_data = query_gemini_api(transcription)

#             return jsonify(structured_data)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#     finally:
#         # Clean up temporary files
#         if os.path.exists(temp_video_file.name):
#             os.remove(temp_video_file.name)


# def transcribe_audio(video_path):
#     """
#     Extract audio from video file and transcribe using Whisper AI.
#     """
#     try:
#         # Extract audio using ffmpeg
#         audio_path = video_path.replace(".mp4", ".wav")
#         command = [
#             "ffmpeg",
#             "-i", video_path,
#             "-q:a", "0",
#             "-map", "a",
#             audio_path
#         ]
#         subprocess.run(command, check=True)
#         print(f"Audio extracted to: {audio_path}")

#         # Transcribe audio using Whisper AI
#         print("Transcribing audio...")
#         result = whisper_model.transcribe(audio_path)

#         # Clean up audio file after transcription
#         if os.path.exists(audio_path):
#             os.remove(audio_path)

#         return result.get("text", "").strip()

#     except Exception as e:
#         print(f"Error in transcription: {e}")
#         return None


# def query_gemini_api(transcription):
#     """
#     Send transcription text to Gemini API and fetch structured recipe information.
#     """
#     try:
#         # Define the structured prompt
#         prompt = (
#             "Analyze the provided cooking video transcription and extract the following structured information:\n"
#             "1. Recipe Name: Identify the name of the dish being prepared.\n"
#             "2. Ingredients List: Extract a detailed list of ingredients with their respective quantities (if mentioned).\n"
#             "3. Steps for Preparation: Provide a step-by-step breakdown of the recipe's preparation process, organized and numbered sequentially.\n"
#             "4. Cooking Techniques Used: Highlight the cooking techniques demonstrated in the video, such as searing, blitzing, wrapping, etc.\n"
#             "5. Equipment Needed: List all tools, appliances, or utensils mentioned, e.g., blender, hot pan, cling film, etc.\n"
#             "6. Nutritional Information (if inferred): Provide an approximate calorie count or nutritional breakdown based on the ingredients used.\n"
#             "7. Serving size: In count of people or portion size.\n"
#             "8. Special Notes or Variations: Include any specific tips, variations, or alternatives mentioned.\n"
#             "9. Festive or Thematic Relevance: Note if the recipe has any special relevance to holidays, events, or seasons.\n"
#             f"Text: {transcription}\n"
#         )

#         # Prepare the payload and headers
#         payload = {
#             "contents": [
#                 {
#                     "parts": [
#                         {"text": prompt}
#                     ]
#                 }
#             ]
#         }
#         headers = {"Content-Type": "application/json"}

#         # Send request to Gemini API
#         print("Querying Gemini API...")
#         response = requests.post(
#             f"{GEMINI_API_ENDPOINT}?key={GEMINI_API_KEY}",
#             json=payload,
#             headers=headers
#         )
#         response.raise_for_status()

#         # Extract and return the structured data
#         data = response.json()
#         return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No result found")

#     except requests.exceptions.RequestException as e:
#         print(f"Error querying Gemini API: {e}")
#         return {"error": str(e)}


# if __name__ == '__main__':
#     app.run(debug=True)



# # Above code is taking mp4 input and converts it on it's own to wav

## Below code requires the user to provide the wav file
import os
import whisper
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from deepgram import DeepgramClient, PrerecordedOptions
import tempfile
import json

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

# Load Whisper AI model at startup
# print("Loading Whisper AI model..., ANIKET")
# whisper_model = whisper.load_model("base")  # Choose model size: tiny, base, small, medium, large
# print("Whisper AI model loaded successfully, ANIKET")


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "success", "message": "API is running successfully!"}), 200


@app.route("/mbsa")
def mbsa():
    return render_template("mbsa.html")


@app.route('/process-audio', methods=['POST'])
def process_audio():
    print("GOT THE PROCESS AUDIO REQUEST, ANIKET")
    
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    print("AUDIO FILE NAME: ", audio_file)

    temp_audio_path = None
    try:
        print("STARTING TRANSCRIPTION, ANIKET")
        
        # Step 1: Save the audio file temporarily to a specific location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio_file:
            temp_audio_path = temp_audio_file.name  # Get the file path
            temp_audio_file.write(audio_file.read())  # Write the uploaded audio to the temp file
        
        print(f"Temporary audio file saved at: {temp_audio_path}")
        
        # Step 2: Transcribe the uploaded audio file synchronously
        transcription = transcribe_audio(temp_audio_path)

        print("BEFORE THE transcription FAILED ERROR, CHECKING IF I GOT THE TRANSCRIPTION", transcription)

        if not transcription:
            return jsonify({"error": "Audio transcription failed"}), 500

        print("GOT THE transcription")

        # Step 3: Generate structured recipe information using Gemini API synchronously
        print("Starting the GEMINI REQUEST TO STRUCTURE IT")
        structured_data = query_gemini_api(transcription)

        print("GOT THE STRUCTURED DATA", structured_data)
        # Step 4: Return the structured data
        return jsonify(structured_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up the temporary WAV file
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            print(f"Temporary WAV file deleted: {temp_audio_path}")



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
                print("Request successful! Processing response.")

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
                print(f"Transcript saved to file: {transcript_file_path}")
                
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
            "Print the transcription in the response as well"
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



