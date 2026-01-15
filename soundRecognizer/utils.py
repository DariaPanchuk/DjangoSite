import tensorflow_hub as hub
import numpy as np
import librosa
import pandas as pd
from deep_translator import GoogleTranslator

_YAMNET_MODEL = None
_CLASS_NAMES = None

def get_model_and_classes():
    global _YAMNET_MODEL, _CLASS_NAMES

    if _YAMNET_MODEL is None:
        print("Завантаження моделі YAMNet... (це може зайняти час)")
        _YAMNET_MODEL = hub.load('https://tfhub.dev/google/yamnet/1')

        class_map_path = _YAMNET_MODEL.class_map_path().numpy()
        if isinstance(class_map_path, bytes):
            class_map_path = class_map_path.decode('utf-8')

        _CLASS_NAMES = pd.read_csv(class_map_path)['display_name'].tolist()
        print("Модель YAMNet завантажено!")

    return _YAMNET_MODEL, _CLASS_NAMES

def analyze_audio(file_path):
    try:
        model, class_names = get_model_and_classes()
        wav_data, sample_rate = librosa.load(file_path, sr=16000, mono=True)
        max_val = np.max(np.abs(wav_data))
        if max_val > 0:
            wav_data = wav_data / max_val

        scores, embeddings, spectrogram = model(wav_data)
        mean_scores = np.mean(scores, axis=0)
        top_n = 10
        top_indices = np.argsort(mean_scores)[::-1][:top_n]
        translator = GoogleTranslator(source='auto', target='uk')

        results = []
        for i in top_indices:
            sound_name = class_names[i]
            probability = mean_scores[i] * 100

            if probability > 5:
                try:
                    ukr_name = translator.translate(sound_name)
                    results.append(f"{ukr_name} ({int(probability)}%)")
                except:
                    results.append(f"{sound_name} ({int(probability)}%)")

        if not results:
            return "Тиша або невідомий звук"

        return ", ".join(results)

    except Exception as e:
        print(f"Audio Error: {e}")
        return "Помилка обробки аудіо"