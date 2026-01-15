import shutil
import tempfile
import os
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import ImageUpload

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageRecognizerViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        try:
            self.url = reverse('imageRecognizer:index')
        except:
            self.url = '/imageRecognizer/'

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_get_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @patch('imageRecognizer.views.classify_image')
    def test_post_upload_image(self, mock_classify):
        mock_classify.return_value = ("Кіт, Ссавець", 98.5)

        tiny_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
            b'\x01\x00\x01\x00\x00\x02\x01\x44\x00\x3b'
        )
        img_file = SimpleUploadedFile("cat.gif", tiny_gif, content_type="image/gif")

        response = self.client.post(self.url, {'image': img_file})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ImageUpload.objects.count(), 1)

        obj = ImageUpload.objects.first()
        self.assertEqual(obj.result, "Кіт, Ссавець")
        mock_classify.assert_called_once()


class ImageRecognizerUtilsTests(TestCase):

    # --- ВИПРАВЛЕНО: Тепер мокаємо os.getenv ---

    @patch('imageRecognizer.utils.os.getenv')
    def test_classify_no_api_key(self, mock_getenv):
        """Перевіряємо випадок, коли ключа немає"""
        from imageRecognizer.utils import classify_image

        # Кажемо системі, що ключа немає (None)
        mock_getenv.return_value = None

        result, score = classify_image("fake_path.jpg")

        # Тепер функція має вийти одразу, не намагаючись відкрити файл
        self.assertEqual(result, "Немає ключа API")
        self.assertEqual(score, 0.0)

    @patch('imageRecognizer.utils.os.getenv')
    @patch('imageRecognizer.utils.requests.post')
    @patch('imageRecognizer.utils.GoogleTranslator')
    def test_classify_success(self, mock_translator, mock_post, mock_getenv):
        """Перевіряємо успішний сценарій"""
        from imageRecognizer.utils import classify_image

        # 1. Даємо фейковий ключ
        mock_getenv.return_value = "TEST_FAKE_KEY"

        # 2. Налаштовуємо відповідь Google
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "responses": [{
                "labelAnnotations": [
                    {"description": "Cat", "score": 0.99}
                ]
            }]
        }
        mock_post.return_value = mock_response

        # 3. Налаштовуємо переклад
        mock_translator.return_value.translate.return_value = "Кіт"

        # 4. Створюємо тимчасовий файл
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"fake data")
            tmp_path = tmp.name

        try:
            label, score = classify_image(tmp_path)

            self.assertEqual(label, "Кіт")

            # 5. Перевіряємо, що в URL пішов саме наш фейковий ключ
            args, _ = mock_post.call_args
            self.assertIn("key=TEST_FAKE_KEY", args[0])

        finally:
            os.remove(tmp_path)