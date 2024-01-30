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

def auth(username, password):
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
            {"role": "system", "content": "You are provided with an image. Examine the visual elements, context, and any text present in the image. Pay close attention to the themes, emotions, and messages conveyed by the image. Based on this comprehensive analysis, generate 10 unique and contextually appropriate comments for Instagram. Ensure each comment is concise, not exceeding 20 characters. For every third comment, include an emoji commonly used on Instagram. All comments should be written in Korean. Your response should consist only of the comments."},
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
                "The content provided consists of a series of images from an album. Please analyze these images carefully, paying special attention to their context and any text they contain. Understand the themes, emotions, and messages conveyed by these images. Based on this in-depth analysis, craft 10 unique and contextually relevant comments suitable for Instagram. Each comment should be concise, not exceeding 20 characters. Incorporate emojis into every third comment, using emojis that are commonly seen on Instagram. All comments should be written in Korean. Please return only the comments.",
                *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::len(base64Frames)//50 if len(base64Frames) >= 50 else 1]),
            ],
        },
    ]
    params = {
        "model": "gpt-4-vision-preview",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 4096,
    }

    result = client.chat.completions.create(**params)
    print(result.choices[0].message.content)
    return result.choices[0].message.content



def video_gen(media_path,frame_skip=50):
    try:
        print(f"Attempting to open video file at: {media_path}")
        media_path_str = str(media_path)  # Explicitly convert to string

        if not os.path.exists(media_path_str):
            raise FileNotFoundError(f"Video file does not exist at {media_path_str}")

        video = cv2.VideoCapture(media_path_str)
        
        if not video.isOpened():
            raise ValueError(f"Unable to open video file at {media_path_str}")

        base64Frames = []
        frame_count = 0
        while video.isOpened():
            success, frame = video.read()
            if not success:
                break
            if frame_count % frame_skip == 0:
                _, buffer = cv2.imencode(".jpg", frame)
                base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
            frame_count += 1

        video.release()
        PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                "The content provided consists of a series of video frames. Please analyze these frames closely, focusing on their context and any text they contain. Understand the overarching themes, emotions, and messages conveyed through these frames. Based on this in-depth analysis, craft 10 unique and contextually relevant comments suitable for Instagram. Each comment should be concise, not exceeding 20 characters. Include emojis in every third comment, choosing emojis that are popular on Instagram. The comments should be formulated in Korean. Please return only the comments.",
                *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::50]),
            ],
        },
        ]
        params = {
            "model": "gpt-4-vision-preview",
            "messages": PROMPT_MESSAGES,
            "max_tokens": 4096,
        }

        result = client.chat.completions.create(**params)
        print(result.choices[0].message.content)
        return result.choices[0].message.content
    except Exception as e:
        if "request too large" in str(e).lower():
            # If the error is due to a large request, retry with fewer frames
            new_frame_skip = frame_skip * 2
            print(f"Request too large, retrying with frame skip: {new_frame_skip}")
            return video_gen(media_path, frame_skip=new_frame_skip)
        else:
            print(f"An error occurred in video_gen: {e}")
            return str(e)

# video_gen("/home/musa/Desktop/insta/withnami_3284820004305749845.mp4")