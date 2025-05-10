from deep_translator import GoogleTranslator
import re
import chardet

input_file = "closecaption_english.txt"
output_file = "closecaption_indonesian_python.txt"

translator = GoogleTranslator(source='en', target='id')

def translate_preserving_tokens(value):
    # Deteksi token khusus
    tokens = re.findall(r'[\{\[\(].*?[\}\]\)]', value)
    token_map = {f"<T{i}>": t for i, t in enumerate(tokens)}

    temp_value = value
    for placeholder, token in token_map.items():
        temp_value = temp_value.replace(token, placeholder)

    try:
        translated = translator.translate(temp_value)
    except Exception as e:
        print(f"❌ Gagal menerjemahkan: '{value}' → {e}")
        return value

    for placeholder, token in token_map.items():
        translated = translated.replace(placeholder, token)

    return translated

def process_line(line, line_number):
    match = re.match(r'(\s*)"([^"]+)"\s+"([^"]*)"', line)
    if match:
        indent, key, value = match.groups()
        if key != "Language":
            print(f"🔄 [{line_number}] Menerjemahkan '{key}': {value}")
            value = translate_preserving_tokens(value)
        return f'{indent}"{key}" "{value}"\n'
    return line

def detect_encoding(filepath):
    with open(filepath, 'rb') as f:
        raw = f.read(10000)
    result = chardet.detect(raw)
    return result['encoding']

def translate_file(input_path, output_path):
    encoding = detect_encoding(input_path)
    print(f"📄 Encoding terdeteksi: {encoding}")

    with open(input_path, 'r', encoding=encoding) as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:
        for i, line in enumerate(infile, 1):
            translated_line = process_line(line, i)
            outfile.write(translated_line)

    print("✅ Terjemahan selesai!")

if __name__ == "__main__":
    translate_file(input_file, output_file)