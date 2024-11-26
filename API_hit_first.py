import requests
import subprocess
import os

# Replace with your Hugging Face Space's URL
url = "https://goodml-dishdecode.hf.space/process-audio"  # Use the updated endpoint

# Path to your local video file
video_file_path = "D:/COURSES/CGAS/Dish-Decode/CHRISTMAS RECIPE_Christmas Beef Wellington.mp4"

# Path for the converted WAV file
wav_file_path = video_file_path.replace(".mp4", ".wav")

try:
    # Step 1: Convert MP4 to WAV using FFmpeg
    print("Converting video to audio (WAV format)...")
    ffmpeg_command = [
        "ffmpeg", "-i", video_file_path, "-q:a", "0", "-map", "a", wav_file_path
    ]
    subprocess.run(ffmpeg_command, check=True)
    print(f"Conversion successful! WAV file saved at: {wav_file_path}")

    # Step 2: Open the WAV file in binary mode and send the POST request
    with open(wav_file_path, "rb") as audio_file:
        print("Sending the WAV file in the POST request...")
        response = requests.post(url, files={"audio": audio_file}, timeout=600) # 10 mins

    # Step 3: Check the response
    if response.status_code == 200:
        print("Request successful! Here's the response:")
        print(response.json())  # If the API returns JSON data
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
