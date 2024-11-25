import requests

# Set the URL of the Flask API
url = "http://127.0.0.1:5000/process-video"

# Specify the video file you want to send
video_file_path = "D:\COURSES\CGAS\Dish-Decode\CHRISTMAS RECIPE_Christmas Beef Wellington.mp4"

# Open the video file and send a POST request to the API
with open(video_file_path, "rb") as video_file:
    response = requests.post(url, files={"video": video_file})

# Print the response from the server
print(response.json())