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