import os
import base64
import requests
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")


def classify_image(img_path):
    if not API_KEY:
        return "Немає ключа API", 0.0

    try:
        with open(img_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        url = f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}"

        payload = {
            "requests": [
                {
                    "image": {"content": base64_image},
                    "features": [{"type": "LABEL_DETECTION", "maxResults": 10}]
                }
            ]
    }

        response = requests.post(url, json=payload)
        result = response.json()

        if "error" in result:
            print(f"Google Error: {result['error']}")
            return "Помилка API", 0.0

        labels = result.get("responses", [])[0].get("labelAnnotations", [])

        if not labels:
            return "Не розпізнано", 0.0

        english_names = [label.get("description") for label in labels]

        text_to_translate = ", ".join(english_names)

        confidence = labels[0].get("score")

        try:
            translator = GoogleTranslator(source='auto', target='uk')
            result_name_uk = translator.translate(text_to_translate)
        except:
            result_name_uk = text_to_translate

        return result_name_uk, round(confidence * 100, 2)

    except Exception as e:
        print(f"Error: {e}")
        return "Помилка", 0.0