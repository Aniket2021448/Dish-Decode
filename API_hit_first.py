# import requests

# # Set the URL of the Flask API
# url = "http://huggingface.co/spaces/GoodML/dishDecode/process-video"



# # Specify the video file you want to send
# video_file_path = "D:/COURSES/CGAS/Dish-Decode/CHRISTMAS RECIPE_Christmas Beef Wellington.mp4"


# # Open the video file and send a POST request to the API
# with open(video_file_path, "rb") as video_file:
#     response = requests.post(url, files={"video": video_file}, verify=False)

# # Print the response from the server
# print(response.json())

import requests

# Replace with your Hugging Face Space's URL
url = "http://huggingface.co/spaces/GoodML/dishDecode/process-video"

# Path to your local video file
video_file_path = "D:/COURSES/CGAS/Dish-Decode/CHRISTMAS RECIPE_Christmas Beef Wellington.mp4"

# Open the video file in binary mode and send the POST request
try:
    with open(video_file_path, "rb") as video_file:
        # Sending the video file as a POST request
        response = requests.post(url, files={"video": video_file}, timeout=60)

    # Check the response
    if response.status_code == 200:
        print("Request successful! Here's the response:")
        print(response.json())  # If the API returns JSON data
    else:
        print(f"Error: Received status code {response.status_code}")
        print(response.text)  # Print the error message if any

except FileNotFoundError:
    print(f"Error: File not found at {video_file_path}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred while making the request: {e}")
