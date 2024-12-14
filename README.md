# Project name: DishDecode
Project description: This project aims to extract and organize structured recipe information from unstructured YouTube videos using audio, text, and visual cues. Combining ML, LLMs, and video analysis, DishDecode delivers PDF-formatted recipes and a searchable database with single-click data download, ensuring easy access to complete recipe details.

Details: 
Our preferred case: YouTube video + English audio description for the recipe (This is the case for the majority of the known chefs making videos like Gordon Ramsay, like this video: https://www.youtube.com/watch?v=xIQXLTFup6M and https://www.youtube.com/watch?v=mhDJNfV7hjk )

We will be extracting the following details from the input video
1. Recipe name
2. Ingredients used
3. Methodology
The above three can be done using the video

Below are a few things that will be done using the LLM, like Gemini and llama3.1/3.2 free-tier versions.
4. Nutritional value (Macros only)
5. Serving size (based on the quantity of ingredients used in other recipes with similar quantity of ingredients)
6. Other recipe-specific details (Extracted based on both the video and LLM knowledge)

Deliverables.
Goal: Create structured data from the Unstructured data like video and texts
1. Output a Pdf formatted recipe
2. Database management of the curated recipe details(In MongoDB or SQL either one of them will be used)
3. Single-click recipe data download allows users to get the recipe data without much scraping hassle.
4. A searchable database to allow users to search for specific recipes based on the recipe name.

Team members and their expertise:
Aniket Panchal: Python, ML and LLMs, Streamlit, PostgreSQL, MongoDB
Drashy: Python, MongoDB, SQL, MERN, Web hostings
Aryan Sharma: Python, MongoDB, MERN, SQL, ML algorithms, Web hostings, Django

Tech stack to be used:
For programming language: Python
For frontend: Either MERN OR Streamlit OR Django 
For hosting purposes: Either local host OR Vercel/Render OR Hugging Face
For database: Either MongoDB OR SQL
For LLM tasks: Gemini APIs, LLAMA APIs,
For Information retrieval from Video: Either WhisperAI OR Google APIs OR self-made Custom code
(We will see which tech stack provides seamless integration with ML and LLM apis)

Possible Challenges
If there is no audio description in the video, we observed two cases.
1. there are no text blocks in the video that can give us information on the recipe. We can open CV or YOLO models for image detection and can get further details using the GPT or Gemini models.

2. Text blocks are present in the video(like this one: https://www.youtube.com/watch?v=j1Jq8JjvSMc ) that can provide us with some information on the recipe. We can extract those blocks using OpenCV object and text detection models to extract information from them, and then we can use the GPT and Gemini LLM-based approaches to complete the relevant information in a structured format.

If time allows, we will try to overcome these challenges.

# HOW TO RUN
1. Download latest python version
2. Download an IDE (VS code, pycharm)
3. Create a new python environment
4. Run this command 
    pip install openai-whisper torch
5. Downlaod ffmpeg from the official website
6. Install the executable zip file as per your OS
7. Extract it in C directory C:/ffmpeg< version number >
8. Open this folder, go in bin folder and copy the path of this location
9. Open environment variables setting on your system -> Edit environment variables
    -> Under system variables -> Click Path -> Click Edit button 
    New window appears -> Click new -> Paste the location path that you copied
    -> Click OK to save
10. Restart the IDE
11. Run the files. 


12. Next, Get the Google Gemini 1.5FLash API key
13. Run this command pip install -q -U google-generativeai



# Testing with deepgram nova for whisperAI API tasks :: Successfull
Step 1: Get the api key from https://console.deepgram.com/
Step 2: pip install "deepgram-sdk>=3.*,<4.0"
Step 3: Get the video converted to .wav at backend using the ffmpeg subprocess command
        and send it over the API to its server, and it returns a transcript for that video
Step 4: Then this transcript is sent over the gemini pro API (google based LLM) along with 
        a promt which tells the LLM to structure the unstructured transcript. 
Step 5: Then this structured information is sent over to the backend which sense the             
        response to frontend.        


# Testing with Text extraction using OpenCV python to extract information from Video 
  which has text description in the video
  https://www.geeksforgeeks.org/text-detection-and-extraction-using-opencv-and-ocr/ 
  
  Download the tesseract-OCR executable file from it's github (https://github.com/UB-Mannheim/tesseract/wiki)
  install in the desired directory, add this directory to the path variables in system environments
  
  This is done to handle the case of videos where audio description is not present in the video
  This, OCR extracts the textual data and present in the video, extracts it from the frames at an interval of 2 seconds. 

# Final response
  It is made using the information from the audio transcription (DeepgramNovo) and video information extraction(tesseract-OCR) combined we are handling a much wider range of types of recipe videos

  The information is combined and then sent to the Gemini1.5 Flash API to get the structured information we desire, 
  with the help of AI we are able to get the data in proper format and meaningful extraction was possible.

  # 🍽️ Recipe Extraction API

This project is a Flask-based API that extracts structured recipe information from cooking tutorial videos! It uses the **Deepgram API** for audio transcription, **Tesseract OCR** for text extraction from video frames, and the **Gemini API** to generate a well-structured recipe document. 🚀

---

## 📦 Project Setup

Follow these steps to set up and run the project on your local machine.

### 1️⃣ Clone the Repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2️⃣ Install Dependencies

Make sure you have Python installed (Python 3.8 or above is recommended). Install the required libraries using pip:

```bash
pip install -r requirements.txt
```

### 3️⃣ Install Tesseract OCR

Ensure **Tesseract OCR** is installed on your system. You can download it here: [Tesseract GitHub](https://github.com/tesseract-ocr/tesseract)

Add Tesseract to your system path and make sure to note its installation location.

#### On Windows:

Add the path to `tesseract.exe` to your environment variables, e.g.:

```bash
C:\Program Files\Tesseract-OCR
```

#### On MacOS (using Homebrew):

```bash
brew install tesseract
```

#### On Ubuntu:

```bash
sudo apt-get install tesseract-ocr
```

### 4️⃣ Setup Environment Variables

Create a `.env` file in the root directory and add your API keys:

```plaintext
FIRST_API_KEY=<Your Gemini API Key>
SECOND_API_KEY=<Your Deepgram API Key>
```

### 5️⃣ Install FFmpeg

This project uses **FFmpeg** for converting MP4 videos to WAV audio. Install it via the following:

#### On MacOS (using Homebrew):

```bash
brew install ffmpeg
```

#### On Ubuntu:

```bash
sudo apt-get install ffmpeg
```

#### On Windows:

Download FFmpeg from [FFmpeg.org](https://ffmpeg.org/download.html) and add it to your system path.

---

## 🚀 Running the Project

Start the Flask server with the following command:

```bash
python app.py
```

If everything is set up correctly, you should see:

```plaintext
 * Running on http://127.0.0.1:5000/
```

---

## 📡 API Endpoints

### ✅ Health Check

**Endpoint:** `GET /`

Check if the API is running.

```bash
curl http://127.0.0.1:5000/
```

**Response:**

```json
{
    "status": "success",
    "message": "API is running successfully!"
}
```

### 🍲 Recipe Extraction

**Endpoint:** `POST /process-video`

#### Request Body:

Send a JSON payload with a video URL:

```json
{
    "videoUrl": "<URL-of-the-cooking-video>"
}
```

#### Example Using `curl`:

```bash
curl -X POST http://127.0.0.1:5000/process-video \
-H "Content-Type: application/json" \
-d '{"videoUrl": "https://example.com/video.mp4"}'
```

#### Sample Response:

```json
{
    "**1. Recipe Name:**": "Beef Wellington",
    "**2. Ingredients List:**": "* Fillet of beef\n* Olive oil\n* Salt\n* Pepper",
    "**3. Steps for Preparation:**": "1. Sear the beef fillet\n2. Brush with mustard",
    "**4. Cooking Techniques Used:**": "* Searing\n* Wrapping",
    "**5. Equipment Needed:**": "* Hot pan\n* Blender",
    "**6. Nutritional Information:**": "High in protein and fat",
    "**7. Serving size:**": "2-4 people",
    "**8. Special Notes or Variations:**": "Use horseradish instead of mustard",
    "**9. Festive or Thematic Relevance:**": "Christmas alternative to roast turkey"
}
```

---

## 🛠️ Key Features

- **Deepgram API** for accurate audio transcription.
- **Tesseract OCR** for extracting text from video frames.
- **Gemini API** for generating structured recipe information.
- **FFmpeg** for seamless MP4-to-WAV conversion.
- Supports both audio and video analysis for enhanced accuracy. 🎯

---

## 🧪 Testing

Use tools like **Postman** or **curl** to test the API endpoints.

---

## 🤝 Contributions

Contributions are welcome! Feel free to submit a pull request or open an issue for any enhancements or bug fixes.

---

## 📄 License

This project is licensed under the MIT License.

---

### 🌟 Happy Coding and Bon Appétit! 👨‍🍳👩‍🍳

