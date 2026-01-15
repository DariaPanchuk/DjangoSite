import shutil
import tempfile
import numpy as np
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import AudioUpload

# Тимчасова папка для файлів
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class SoundRecognizerViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Переконайтеся, що URL правильний
        try:
            self.url = reverse('soundRecognizer:index')
        except:
            self.url = '/soundRecognizer/'

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_get_view(self):
        """Перевірка відкриття сторінки"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @patch('soundRecognizer.views.analyze_audio')
    def test_post_upload_audio(self, mock_analyze):
        """Тест завантаження через View (mock самої функції аналізу)"""
        # Імітуємо відповідь AI
        mock_analyze.return_value = "Гавкіт (90%), Собака (85%)"

        # Створюємо фейковий аудіофайл
        audio_file = SimpleUploadedFile("dog.wav", b"fake_audio_data", content_type="audio/wav")

        response = self.client.post(self.url, {'audio': audio_file})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AudioUpload.objects.count(), 1)

        obj = AudioUpload.objects.first()
        self.assertEqual(obj.result, "Гавкіт (90%), Собака (85%)")
        self.assertEqual(obj.title, "dog.wav")


class SoundRecognizerUtilsTests(TestCase):
    """
    Тести для utils.py.
    Тут найцікавіше: ми підміняємо TensorFlow, Librosa і Pandas.
    """

    @patch('soundRecognizer.utils.hub.load')  # Мокаємо завантаження моделі
    @patch('soundRecognizer.utils.pd.read_csv')  # Мокаємо читання класів
    @patch('soundRecognizer.utils.librosa.load')  # Мокаємо читання файлу
    @patch('soundRecognizer.utils.GoogleTranslator')  # Мокаємо перекладач
    def test_analyze_audio_success(self, mock_translator, mock_librosa, mock_pandas, mock_hub):
        from soundRecognizer.utils import analyze_audio, _YAMNET_MODEL

        # 0. Скидаємо кеш моделі (бо ми змінили код на Singleton)
        import soundRecognizer.utils
        soundRecognizer.utils._YAMNET_MODEL = None
        soundRecognizer.utils._CLASS_NAMES = None

        # 1. Налаштовуємо YAMNet (TensorFlow)
        mock_model_instance = MagicMock()
        # Модель повертає 3 значення: scores, embeddings, spectrogram
        # Scores: (N, 521) - де 521 це кількість класів
        # Зробимо так, щоб 0-й клас мав високу ймовірність
        fake_scores = np.zeros((1, 521))
        fake_scores[0, 0] = 0.99  # 99% для першого класу

        mock_model_instance.return_value = (fake_scores, None, None)
        # Налаштовуємо class_map_path
        mock_model_instance.class_map_path.return_value.numpy.return_value = b'fake_path.csv'

        mock_hub.return_value = mock_model_instance

        # 2. Налаштовуємо імена класів (Pandas)
        # Створимо фейковий DataFrame
        mock_df = MagicMock()
        # Нехай 0-й клас це "Dog Bark"
        # Заповнимо список 521 елементом, щоб не було помилки index out of bounds
        fake_classes = ["Dog Bark"] + ["Noise"] * 520
        mock_df.__getitem__.return_value.tolist.return_value = fake_classes
        mock_pandas.return_value = mock_df

        # 3. Налаштовуємо аудіо (Librosa)
        # Повертає (data, sample_rate)
        mock_librosa.return_value = (np.array([0.1, 0.2, 0.3]), 16000)

        # 4. Налаштовуємо перекладач
        mock_trans_instance = mock_translator.return_value
        mock_trans_instance.translate.return_value = "Гавкіт собаки"

        # --- ЗАПУСК ---
        result = analyze_audio("dummy_path.wav")

        # --- ПЕРЕВІРКА ---
        # 0.99 * 100 = 99
        self.assertIn("Гавкіт собаки (99%)", result)

        # Перевіряємо, що бібліотеки викликалися
        mock_hub.assert_called_once()
        mock_librosa.assert_called_once()

    @patch('soundRecognizer.utils.librosa.load')
    def test_analyze_audio_error(self, mock_librosa):
        """Тест обробки помилок (наприклад, пошкоджений файл)"""
        from soundRecognizer.utils import analyze_audio

        # Librosa викидає помилку
        mock_librosa.side_effect = Exception("File corrupted")

        result = analyze_audio("bad_file.wav")

        self.assertEqual(result, "Помилка обробки аудіо")