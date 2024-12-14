import yt_dlp

URL = 'https://www.youtube.com/watch?v=MJr9g-QMJ8I'
SAVE_PATH = 'D:/COURSES/CGAS/Dish-Decode/Youtube_Downloads'

options = {
    'outtmpl': f'{SAVE_PATH}/%(title)s.%(ext)s',
    'format': 'best'
}

with yt_dlp.YoutubeDL(options) as ydl:
    ydl.download([URL])
