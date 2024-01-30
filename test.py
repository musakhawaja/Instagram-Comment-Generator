from instagrapi import Client
from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
import cv2
from pathlib import Path


load_dotenv()
client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))
cl = Client()

def auth(username="ag.ha2308", password="kkjhjkk"):
    username="ag.ha2308"
    password="kkjhjkk"
    try:
        cl.login(username, password)
        return True
    except Exception as e:
        print(f"Login failed: {e}")
        return False


def media_download(url,option):
    media_pk = cl.media_pk_from_url(url)
    if option=="Photo":
        media_path = cl.photo_download(media_pk)
    elif option == "Reel":
        media_path = cl.video_download(media_pk)
    elif option == "Album":   
       media_path = cl.album_download(media_pk)
    return media_path

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def image_gen(base64_image):
  completion = client.chat.completions.create(
      model="gpt-4-vision-preview",
      messages=[
          {"role": "system", "content": "The content provided to you is an Instagram post. Analyze the content provided and suggest 10 different comments for Instagram. Each comment should be less than 20 charachters. Only use emojis for every 3rd comment and use emojis that can be used on instagram. The comments must be in Korean. Only return the comments"},
          {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}
      ],
      max_tokens=4096
  )

  result = completion.choices[0].message.content
  print(result)
  return result

def album_gen(image_paths):
    base64Frames = []
    for image_path in image_paths:
        frame = cv2.imread(image_path)
        if frame is None:
            continue
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                "The content provided to you is an Instagram post. Analyze the content provided and suggest 10 different comments for Instagram. Each comment should be less than 20 charachters. Include emojis in every 3rd comment and use emojis that can be used on instagram. The comments must be in Korean. Only return the comments",
                *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::len(base64Frames)//50 if len(base64Frames) >= 50 else 1]),
            ],
        },
    ]
    params = {
        "model": "gpt-4-vision-preview",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 200,
    }

    result = client.chat.completions.create(**params)
    print(result.choices[0].message.content)
    return result.choices[0].message.content



def video_gen(media_path):
    try:
        print(f"Attempting to open video file at: {media_path}")
        media_path_str = str(media_path)  # Explicitly convert to string

        if not os.path.exists(media_path_str):
            raise FileNotFoundError(f"Video file does not exist at {media_path_str}")

        video = cv2.VideoCapture(media_path_str)
        
        if not video.isOpened():
            raise ValueError(f"Unable to open video file at {media_path_str}")

        base64Frames = []
        while video.isOpened():
            success, frame = video.read()
            if not success:
                break
            _, buffer = cv2.imencode(".jpg", frame)
            base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

        video.release()
        PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                "The content provided to you is an Instagram post. Analyze the content provided and suggest 10 different comments for Instagram. Each comment should be less than 20 charachters. Include emojis in every 3rd comment and use emojis that can be used on instagram. The comments must be in Korean. Only return the comments",
                *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::50]),
            ],
        },
        ]
        params = {
            "model": "gpt-4-vision-preview",
            "messages": PROMPT_MESSAGES,
            "max_tokens": 200,
        }

        result = client.chat.completions.create(**params)
        print(result.choices[0].message.content)
        return result.choices[0].message.content
    except Exception as e:
        print(f"An error occurred in video_gen: {e}")
        return str(e)


# auth()
# paths = media_download(url="https://www.instagram.com/p/C2hsw-irYAk/?img_index=1",option="Album")
# # print(path)
# # img = encode_image(path)
# # image_gen(img)
# path_strings = [str(path) for path in paths]
# path_strings
# album_gen(path_strings)
video_gen("/home/musa/Desktop/insta/christmas_nail2_3289870297142645854.mp4")