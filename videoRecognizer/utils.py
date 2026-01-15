import cv2
import numpy as np
import yt_dlp
import os
import uuid
from django.conf import settings
from tensorflow.keras.preprocessing import image as keras_image
from collections import Counter
from tensorflow.keras.applications import EfficientNetV2B0
from tensorflow.keras.applications.efficientnet_v2 import preprocess_input, decode_predictions
from deep_translator import GoogleTranslator

_VIDEO_MODEL = None

def get_model():
    global _VIDEO_MODEL
    if _VIDEO_MODEL is None:
        print("Завантаження моделі EfficientNetV2B0...")
        _VIDEO_MODEL = EfficientNetV2B0(weights='imagenet', include_top=True)
    return _VIDEO_MODEL

def download_video_temp(web_url):
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_videos')
    os.makedirs(temp_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(temp_dir, filename)

    ydl_opts = {
        'format': 'best[ext=mp4][height<=720]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'noplaylist': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(web_url, download=True)
            return output_path, info.get('title')
    except Exception as e:
        print(f"Download Error: {e}")
        return None, None


def analyze_video_file(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return "Файл пошкоджено або формат не підтримується"

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or fps != fps: fps = 24

    try:
        model = get_model()
    except Exception as e:
        return f"Помилка завантаження моделі: {e}"

    found_objects = []
    frame_count = 0
    process_interval = int(fps)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % process_interval == 0:
            try:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_resized = cv2.resize(frame_rgb, (224, 224))
                img_array = keras_image.img_to_array(img_resized)
                img_array = np.expand_dims(img_array, axis=0)
                img_array = preprocess_input(img_array)

                preds = model.predict(img_array, verbose=0)
                decoded = decode_predictions(preds, top=1)[0][0]
                found_objects.append(decoded[1])
            except Exception as e:
                print(f"Frame Error: {e}")

        frame_count += 1
        if frame_count > fps * 120:
            break

    cap.release()

    if not found_objects:
        return "Нічого не знайдено"

    counts = Counter(found_objects)
    most_common = counts.most_common(20)

    translator = GoogleTranslator(source='auto', target='uk')
    translated_results = []

    for obj, count in most_common:
        clean_name = obj.replace('_', ' ')
        try:
            ukr_text = translator.translate(clean_name)
            translated_results.append(f"{ukr_text} ({count})")
        except:
            translated_results.append(f"{clean_name} ({count})")

    return ", ".join(translated_results)