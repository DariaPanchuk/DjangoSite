import shutil
import tempfile
import os
import numpy as np
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import VideoUpload

# Тимчасова папка
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class VideoRecognizerViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        try:
            self.url = reverse('videoRecognizer:index')
        except:
            self.url = '/videoRecognizer/'

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_get_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @patch('videoRecognizer.views.analyze_video_file')
    def test_post_upload_file(self, mock_analyze):
        """Тест завантаження файлу (View)"""
        mock_analyze.return_value = "Кіт (5), Собака (2)"

        video_file = SimpleUploadedFile("test.mp4", b"fake_mp4_data", content_type="video/mp4")

        response = self.client.post(self.url, {'video': video_file})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(VideoUpload.objects.count(), 1)

        obj = VideoUpload.objects.first()
        self.assertEqual(obj.result, "Кіт (5), Собака (2)")
        mock_analyze.assert_called_once()

    @patch('videoRecognizer.views.download_video_temp')
    @patch('videoRecognizer.views.analyze_video_file')
    def test_post_upload_url_success(self, mock_analyze, mock_download):
        """Тест завантаження через URL (View)"""
        # Створюємо реальний тимчасовий файл, бо View перевіряє os.path.exists
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"fake video")
            tmp_path = tmp.name

        try:
            # Моки
            mock_download.return_value = (tmp_path, "YouTube Test Video")
            mock_analyze.return_value = "Автомобіль (10)"

            response = self.client.post(self.url, {'url': 'http://youtube.com/fake'})

            self.assertEqual(response.status_code, 200)
            self.assertEqual(VideoUpload.objects.count(), 1)

            obj = VideoUpload.objects.first()
            self.assertEqual(obj.title, "YouTube Test Video")
            self.assertEqual(obj.result, "Автомобіль (10)")

        finally:
            # View має видалити файл, але про всяк випадок підчистимо
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class VideoRecognizerUtilsTests(TestCase):
    """
    Тести для utils.py.
    Тут ми перевіряємо логіку обробки кадрів, мокаючи OpenCV та Keras.
    """

    @patch('videoRecognizer.utils.cv2.VideoCapture')  # Мокаємо відеозахват
    @patch('videoRecognizer.utils.get_model')  # Мокаємо отримання моделі
    @patch('videoRecognizer.utils.GoogleTranslator')  # Мокаємо перекладач
    @patch('videoRecognizer.utils.decode_predictions')  # Мокаємо декодування результатів Keras
    def test_analyze_video_logic(self, mock_decode, mock_translator, mock_get_model, mock_cv2_cap):
        from videoRecognizer.utils import analyze_video_file, _VIDEO_MODEL

        # Скидаємо глобальну модель для чистоти
        import videoRecognizer.utils
        videoRecognizer.utils._VIDEO_MODEL = None

        # 1. Налаштування OpenCV (cv2)
        mock_cap_instance = MagicMock()
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.get.return_value = 1.0  # FPS = 1.0 (щоб кожен кадр оброблявся)

        # Імітуємо цикл читання кадрів: 
        # 1-й виклик -> (True, frame_data)
        # 2-й виклик -> (False, None) -> кінець відео
        fake_frame = np.zeros((224, 224, 3), dtype=np.uint8)
        mock_cap_instance.read.side_effect = [(True, fake_frame), (False, None)]

        mock_cv2_cap.return_value = mock_cap_instance

        # 2. Налаштування Моделі (TensorFlow/Keras)
        mock_model_instance = MagicMock()
        mock_model_instance.predict.return_value = "fake_preds"
        mock_get_model.return_value = mock_model_instance

        # 3. Налаштування Decode Predictions (щоб Keras повернув "cat")
        # decode_predictions повертає список списків кортежів: [[(id, 'label', score)]]
        mock_decode.return_value = [[('n123', 'cat', 0.99)]]

        # 4. Налаштування перекладача
        mock_trans_instance = mock_translator.return_value
        mock_trans_instance.translate.return_value = "Кіт"

        # --- ЗАПУСК ---
        result = analyze_video_file("dummy_path.mp4")

        # --- ПЕРЕВІРКА ---
        self.assertIn("Кіт", result)
        self.assertIn("(1)", result)  # Знайдено 1 раз

        mock_cv2_cap.assert_called()
        mock_get_model.assert_called()

    @patch('videoRecognizer.utils.yt_dlp.YoutubeDL')
    def test_download_video_temp(self, mock_ydl):
        """Тест завантажувача (mock yt-dlp)"""
        from videoRecognizer.utils import download_video_temp

        # Налаштовуємо мок контекстного менеджера (with yt_dlp.YoutubeDL...)
        mock_ydl_instance = mock_ydl.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.return_value = {'title': 'Test Video Title'}

        path, title = download_video_temp('http://fake.url')

        self.assertEqual(title, 'Test Video Title')
        self.assertTrue(path.endswith('.mp4'))
        # Перевіряємо, що шлях веде в папку temp_videos
        self.assertIn('temp_videos', path)