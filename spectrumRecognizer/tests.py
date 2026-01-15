import shutil
import tempfile
import numpy as np
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import SpectrumAudio

# Тимчасова папка для тестів
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class SpectrumRecognizerViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Перевірте, чи ім'я 'index' збігається з urls.py
        try:
            self.url = reverse('spectrumRecognizer:index')
        except:
            self.url = '/spectrumRecognizer/'

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_get_view(self):
        """Перевірка доступності сторінки"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'spectrumRecognizer/index.html')

    @patch('spectrumRecognizer.views.analyze_signal_data')
    def test_post_upload_audio(self, mock_analyze):
        """
        Тест завантаження файлу.
        Ми мокаємо аналіз, щоб не запускати математику FFT.
        """
        # Імітуємо результат аналізу (рядок, як повертає utils.py)
        mock_analyze.return_value = "50.0 Hz (10.5%), 100.0 Hz (5.2%)"

        # Створюємо фейковий файл
        audio_file = SimpleUploadedFile("signal.wav", b"fake_audio_bytes", content_type="audio/wav")

        response = self.client.post(self.url, {'audio': audio_file})

        self.assertEqual(response.status_code, 200)

        # Перевіряємо запис в БД
        self.assertEqual(SpectrumAudio.objects.count(), 1)
        obj = SpectrumAudio.objects.first()

        self.assertEqual(obj.title, "signal.wav")
        self.assertEqual(obj.result_text, "50.0 Hz (10.5%), 100.0 Hz (5.2%)")

        # Переконуємось, що View викликала функцію аналізу
        mock_analyze.assert_called_once()


class SpectrumRecognizerUtilsTests(TestCase):
    """
    Тестуємо математику спектрального аналізу.
    Мокаємо librosa.load, але дозволяємо numpy рахувати справжній FFT.
    """

    @patch('spectrumRecognizer.utils.librosa.load')
    def test_analyze_signal_logic(self, mock_librosa):
        from spectrumRecognizer.utils import analyze_signal_data

        # --- ПІДГОТОВКА ДАНИХ ---
        # Створимо простий штучний сигнал: синусоїда
        # Це дозволить перевірити, чи numpy рахує правильно
        sr = 100  # Частота дискретизації (маленька для простоти)
        t = np.linspace(0, 1, sr)  # 1 секунда
        # Сигнал: проста константа (DC offset) = 1.0
        # FFT константи дасть пік на 0 Hz
        y = np.ones_like(t)

        # Налаштовуємо мок: librosa повертає (сигнал, частота)
        mock_librosa.return_value = (y, sr)

        # --- ВИКОНАННЯ ---
        # Передаємо будь-який шлях, бо librosa замокана
        result = analyze_signal_data("dummy_path.wav")

        # --- ПЕРЕВІРКА ---
        # Результат має бути рядком
        self.assertIsInstance(result, str)

        # Оскільки сигнал постійний (DC), основна частота має бути 0.0 Hz
        self.assertIn("0.0 Hz", result)

        # Перевіряємо, що відсотки теж пораховані (наявність знака %)
        self.assertIn("%", result)

    @patch('spectrumRecognizer.utils.librosa.load')
    def test_analyze_signal_error(self, mock_librosa):
        """Тест на випадок помилки (битий файл)"""
        from spectrumRecognizer.utils import analyze_signal_data

        # Librosa кидає помилку
        mock_librosa.side_effect = Exception("Corrupted WAV")

        result = analyze_signal_data("bad_file.wav")

        self.assertEqual(result, "Error: Corrupted WAV")