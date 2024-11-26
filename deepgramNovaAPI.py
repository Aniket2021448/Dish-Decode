from deepgram import DeepgramClient, PrerecordedOptions


import requests
import subprocess
import os
import json
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Fetch the API key from the .env file
API_KEY = os.getenv("SECOND_API_KEY")

# Ensure the API key is loaded correctly
if not API_KEY:
    raise ValueError("API Key not found. Make sure it is set in the .env file.")

# The API key we created in step 3
DEEPGRAM_API_KEY = API_KEY


# Path to your local video file
video_file_path = "D:/COURSES/CGAS/Dish-Decode/CHRISTMAS RECIPE_Christmas Beef Wellington.mp4"

# Path for the converted WAV file
wav_file_path = video_file_path.replace(".mp4", ".wav")


# Replace with your file path
# PATH_TO_FILE = '.wav'

def main():
    try:
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        # Step 1: Convert MP4 to WAV using FFmpeg
        print("Converting video to audio (WAV format)...")
        ffmpeg_command = [
            "ffmpeg", "-i", video_file_path, "-q:a", "0", "-map", "a", wav_file_path
        ]
        subprocess.run(ffmpeg_command, check=True)
        print(f"Conversion successful! WAV file saved at: {wav_file_path}")

        PATH_TO_FILE = wav_file_path

        with open(PATH_TO_FILE, 'rb') as buffer_data:
            payload = { 'buffer': buffer_data }

            options = PrerecordedOptions(
                smart_format=True, model="nova-2", language="en-US"
            )

            response = deepgram.listen.prerecorded.v('1').transcribe_file(payload, options)
            if response:
                print("Request successful! Here's the response:")
                # print()
                print("response type:",type(response))
                print()
                        # Convert the response to a JSON string
                try:
                    data_str = response.to_json(indent=4)
                    print("data type:", type(data_str))
                except AttributeError as e:
                    print(f"Error converting response to JSON string: {e}")
                    return  # Exit the function if conversion fails

                # Parse the JSON string to a Python dictionary
                try:
                    data = json.loads(data_str)
                    print("Parsed data type:", type(data))
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON string: {e}")
                    return  # Exit the function if parsing fails

                # Extract the transcript
                transcript = data["results"]["channels"][0]["alternatives"][0]["transcript"]
                print("Transcript:", transcript)
                print(type(transcript))


                # transcript = data["results"]["channels"][0]["alternatives"][0]["transcript"]
                # print(transcript)

                # Path to the text file
                output_text_file = "deepGramNovaTranscript.txt"

                # Write the transcript to the text file
                with open(output_text_file, "w", encoding="utf-8") as file:
                    file.write(transcript)

                print(f"Transcript saved to: {output_text_file}")

            else:
                print(f"Error: Received status code {response.status_code}")
                print(response.text)  # Print the error message if any


    except FileNotFoundError:
        print(f"Error: File not found at {video_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request: {e}")
    finally:
        # Step 4: Clean up the WAV file after the request
        if os.path.exists(wav_file_path):
            os.remove(wav_file_path)
            print(f"Temporary WAV file deleted: {wav_file_path}")

if __name__ == '__main__':
    main()


