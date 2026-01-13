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
from deep_translator import GoogleTranslator  # <--- Імпорт перекладача

model = EfficientNetV2B0(weights='imagenet', include_top=True)

def download_video_temp(web_url):
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_videos')
    os.makedirs(temp_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(temp_dir, filename)

    ydl_opts = {
        'format': 'best[ext=mp4][height<=480]',
        'outtmpl': output_path,
        'quiet': True,
        'noplaylist': True,
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

    found_objects = []
    frame_count = 0
    process_interval = int(fps)  # 1 кадр на секунду

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
        if frame_count > fps * 120:  # Ліміт 2 хв
            break

    cap.release()

    if not found_objects:
        return "Нічого не знайдено"

    counts = Counter(found_objects)
    most_common = counts.most_common(20)  # Топ-10 об'єктів

    translator = GoogleTranslator(source='auto', target='uk')
    translated_results = []

    for obj, count in most_common:
        clean_name = obj.replace('_', ' ')
        try:
            ukr_text = translator.translate(clean_name)
            translated_results.append(f"{ukr_text} ({count})")
        except:
            # Якщо переклад не вдався, лишаємо англійською
            translated_results.append(f"{clean_name} ({count})")

    return ", ".join(translated_results)