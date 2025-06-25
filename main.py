import os
import pdfplumber
import json
from dotenv import load_dotenv
from ocr_utils import extract_text_from_image
from data_extractor import extract_passport_fields

load_dotenv()

DOCS_DIR = "docs"
DATA_DIR = "data"

def process_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text and page_text.strip() != "":
                print(f"Página {page_number+1}: texto extraído con pdfplumber")
                text += page_text + "\n"
            else:
                print(f"Página {page_number+1}: no hay texto — haciendo OCR")
                # Convertir la página en imagen (PIL Image)
                image = page.to_image(resolution=300).original
                import pytesseract
                ocr_text = pytesseract.image_to_string(image)
                text += ocr_text + "\n"
    return text

def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    for filename in os.listdir(DOCS_DIR):
        file_path = os.path.join(DOCS_DIR, filename)

        if filename.lower().endswith(".pdf"):
            print(f"\n=============================")
            print(f"Procesando PDF: {filename}")
            text = process_pdf(file_path)
        elif filename.lower().endswith((".jpg", ".jpeg", ".png")):
            print(f"\n=============================")
            print(f"Procesando imagen: {filename}")
            text = extract_text_from_image(file_path)
        else:
            print(f"Ignorando archivo: {filename}")
            continue

        print("Texto extraído:")
        print(text)

        fields = extract_passport_fields(text)
        print("Campos extraídos:")
        print(fields)

        # Convertir response a JSON limpio
        fields_str = fields.content
        fields_str = fields_str.replace("```json", "").replace("```", "").strip()

        try:
            fields_json = json.loads(fields_str)
        except json.JSONDecodeError:
            print("❌ Error al convertir a JSON — se guarda como pasaporte_sin_nombre.json")
            output_path = os.path.join(DATA_DIR, f"pasaporte_sin_nombre.json")
            with open(output_path, "w", encoding="utf-8") as file:
                json.dump({"texto_extraido": text}, file, indent=4, ensure_ascii=False)
            continue

        nombre = fields_json.get("nombre", "").strip()

        if not nombre:
            print("❌ No se detectó nombre — se guarda como pasaporte_sin_nombre.json")
            output_path = os.path.join(DATA_DIR, f"pasaporte_sin_nombre.json")
        else:
            nombre_clean = nombre.replace(" ", "_").lower()
            output_path = os.path.join(DATA_DIR, f"pasaporte_{nombre_clean}.json")
            print(f"✅ Nombre detectado: {nombre}")

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(fields_json, file, indent=4, ensure_ascii=False)

        print(f"✅ Guardado en: {output_path}")

if __name__ == "__main__":
    main()
