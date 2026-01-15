import shutil
import tempfile
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from unittest.mock import patch, MagicMock
from .models import CodeFiles

# Створюємо тимчасову папку для медіа-файлів, щоб не смітити в реальній папці
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CodeRecognizerTests(TestCase):

    def setUp(self):
        # Цей код виконується перед кожним тестом
        self.client = Client()
        self.url = reverse('codeRecognizer:index')  # Отримуємо URL за ім'ям

    def tearDown(self):
        # Цей код виконується після кожного тесту (чистимо файли)
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    # --- ТЕСТИ МОДЕЛІ ---
    def test_model_str_method(self):
        """Перевіряємо, що __str__ повертає назву або дефолтне значення"""
        file = SimpleUploadedFile("test_code.py", b"print('hello')")
        obj = CodeFiles.objects.create(code_file=file, title="Мій скрипт")

        self.assertEqual(str(obj), "Мій скрипт")

        obj_no_title = CodeFiles.objects.create(code_file=file)
        self.assertEqual(str(obj_no_title), "Code File")

    # --- ТЕСТИ VIEW (Головна логіка) ---

    def test_get_index_view(self):
        """Перевіряємо, що сторінка відкривається (код 200)"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'codeRecognizer/index.html')

    @patch('codeRecognizer.views.generate_docs')  # <--- ГОЛОВНИЙ ФОКУС
    def test_upload_file_successful(self, mock_generate_docs):
        """
        Тестуємо завантаження файлу.
        Ми 'мокаємо' функцію generate_docs, щоб не запускати справжній AI.
        """
        # 1. Налаштовуємо імітацію: нехай AI 'поверне' цей текст
        mock_generate_docs.return_value = "Це тестова документація від фейкового AI."

        # 2. Створюємо фейковий файл
        fake_file = SimpleUploadedFile("script.py", b"def foo(): pass", content_type="text/x-python")

        # 3. Відправляємо POST запит
        response = self.client.post(self.url, {'code_file': fake_file})

        # 4. Перевірки
        self.assertEqual(response.status_code, 200)  # Сторінка перезавантажилась успішно

        # Перевіряємо, чи запис з'явився в базі
        self.assertEqual(CodeFiles.objects.count(), 1)
        saved_obj = CodeFiles.objects.first()

        # Перевіряємо, чи збереглись дані
        self.assertEqual(saved_obj.title, "script.py")
        # Найважливіше: чи записався результат нашого 'фейкового' AI в базу
        self.assertEqual(saved_obj.generated_docs, "Це тестова документація від фейкового AI.")

        # Перевіряємо, що функція AI дійсно викликалася один раз
        mock_generate_docs.assert_called_once()

    # --- ТЕСТИ UTILS (Логіка AI ізольовано) ---

    @patch('codeRecognizer.utils.code_model')  # Мокаємо модель
    @patch('codeRecognizer.utils.code_tokenizer')  # Мокаємо токенізатор
    @patch('codeRecognizer.utils.GoogleTranslator')  # Мокаємо перекладач
    def test_generate_docs_logic(self, mock_translator, mock_tokenizer, mock_model):
        """
        Тестуємо саму функцію generate_docs, але без реальних обчислень.
        Перевіряємо ланцюжок викликів: читання -> токени -> генерація -> переклад.
        """
        from codeRecognizer.utils import generate_docs

        # Налаштування моків (імітації)
        # 1. Налаштовуємо "Tokenazer"
        mock_tokenizer.return_value.input_ids = "fake_input_ids"
        mock_tokenizer.decode.return_value = "This function calculates sum."  # Англійський текст

        # 2. Налаштовуємо "Model"
        mock_model.generate.return_value = ["fake_output_ids"]

        # 3. Налаштовуємо "GoogleTranslator"
        mock_translator_instance = mock_translator.return_value
        mock_translator_instance.translate.return_value = "Ця функція рахує суму."  # Український текст

        # Створюємо реальний файл для тесту
        with tempfile.NamedTemporaryFile(suffix=".py", mode='w+', encoding='utf-8', delete=False) as tmp:
            tmp.write("def sum(a, b): return a + b")
            tmp_path = tmp.name

        try:
            # ВИКЛИК ФУНКЦІЇ
            result = generate_docs(tmp_path)

            # ПЕРЕВІРКИ
            self.assertEqual(result, "Ця функція рахує суму.")

            # Перевіряємо, чи викликався перекладач
            mock_translator.assert_called_with(source='auto', target='uk')
            mock_translator_instance.translate.assert_called_with("This function calculates sum.")

        finally:
            # Видаляємо тимчасовий файл
            import os
            if os.path.exists(tmp_path):
                os.remove(tmp_path)