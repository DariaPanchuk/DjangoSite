from transformers import RobertaTokenizer, T5ForConditionalGeneration
from deep_translator import GoogleTranslator
import os
import textwrap

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

        if len(code_content) < 50:
            return "Файл занадто малий для аналізу."

        chunks = textwrap.wrap(code_content, 1000, break_long_words=False, replace_whitespace=False)
        combined_summary = []

        for chunk in chunks:
            try:
                input_ids = code_tokenizer(chunk, return_tensors="pt").input_ids

                generated_ids = code_model.generate(
                    input_ids,
                    max_length=100,
                    min_length=20,
                    num_beams=8,
                    no_repeat_ngram_size=2,
                    early_stopping=True
                )

                summary_part = code_tokenizer.decode(generated_ids[0], skip_special_tokens=True)
                combined_summary.append(summary_part)
            except Exception as e:
                print(f"Error processing chunk: {e}")
                continue

        explanation_en = " ".join(combined_summary)

        try:
            if len(explanation_en) > 4500:
                explanation_en = explanation_en[:4500] + "..."

            translated = GoogleTranslator(source='en', target='uk').translate(explanation_en)
            return translated
        except Exception as trans_e:
            return f"{explanation_en} (Помилка перекладу: {trans_e})"

    except Exception as e:
        return f"AI Error: {str(e)}"