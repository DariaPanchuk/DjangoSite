from transformers import RobertaTokenizer, T5ForConditionalGeneration
from deep_translator import GoogleTranslator
import os

CODE_MODEL_NAME = "Salesforce/codet5-base-multi-sum"
print("Loading Code Analysis Model... please wait.")
try:
    code_tokenizer = RobertaTokenizer.from_pretrained(CODE_MODEL_NAME)
    code_model = T5ForConditionalGeneration.from_pretrained(CODE_MODEL_NAME)
    print("Code Model Loaded!")
except Exception as e:
    print(f"Failed to load Code Model: {e}")
    code_tokenizer, code_model = None, None

def generate_docs(file_path):
    if not code_tokenizer or not code_model:
        return "Помилка: Модель аналізу коду не завантажена."

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code_content = f.read()

        input_text = code_content[:2000]
        input_ids = code_tokenizer(input_text, return_tensors="pt").input_ids

        generated_ids = code_model.generate(
            input_ids,
            max_length=300,
            min_length=50,
            num_beams=8,
            no_repeat_ngram_size=2,
            early_stopping=True
        )
        explanation_en = code_tokenizer.decode(generated_ids[0], skip_special_tokens=True)

        try:
            translated = GoogleTranslator(source='auto', target='uk').translate(explanation_en)
            return translated
        except Exception as trans_e:
            return f"{explanation_en} (Помилка перекладу: {trans_e})"

    except Exception as e:
        return f"AI Error: {str(e)}"