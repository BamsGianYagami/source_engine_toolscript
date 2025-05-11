import re
import chardet
from deep_translator import GoogleTranslator

input_file = "closecaption_english.txt"
output_file = "closecaption_indonesian.txt"
translator = GoogleTranslator(source='en', target='id')

PHRASE_WHITELIST = [
    "Combine", "Dog", "City 17", "Dr. Breen", "Vortigaunt", "Black Mesa",
    "Lambda", "Strider", "Headcrab", "Barnacle", "Alyx", "Gordon", "Freeman", "Kleiner",
    "Ravenholm", "Citadel", "Hunters"
]

def detect_encoding(filepath):
    with open(filepath, 'rb') as f:
        raw = f.read(10000)
    result = chardet.detect(raw)
    return result['encoding']

# Fungsi untuk melindungi frasa khusus dan menggantinya dengan karakter khusus
def protect_phrases(text):
    protected_map = {}  # Untuk menyimpan pemetaan dengan frasa asli
    phrase_id = 0  # ID untuk setiap frasa

    # Membuat pola regex untuk mencocokkan frasa dari whitelist, termasuk tanda baca di akhir
    pattern = r'(\s|^|[^\w])(' + '|'.join(re.escape(phrase) for phrase in PHRASE_WHITELIST) + r')(\s|$|[^\w])'

    # Fungsi untuk mengganti frasa dengan karakter khusus
    def replacer(match):
        nonlocal phrase_id
        original_phrase = match.group(2)  # Ambil frasa yang ditemukan
        key = f"#@@#{phrase_id}#"  # Gunakan karakter khusus untuk melindungi frasa
        protected_map[key] = original_phrase  # Simpan pemetaan ID dan frasa asli
        phrase_id += 1  # Increment ID untuk frasa berikutnya
        return f"{match.group(1)}{key}{match.group(3)}"  # Pastikan spasi dan tanda baca tetap terjaga

    # Ganti semua frasa yang cocok dengan karakter khusus
    protected_text = re.sub(pattern, replacer, text, flags=re.IGNORECASE)
    return protected_text, protected_map

# Fungsi untuk mengembalikan frasa yang dilindungi ke bentuk aslinya setelah terjemahan
def restore_protected_phrases(text, protected_map):
    for key, value in protected_map.items():
        text = text.replace(key, value)  # Ganti karakter khusus dengan frasa asli
    return text

def translate_parts(value):
    # Pisahkan bagian <tag> [deskripsi] kalimat
    tag_matches = re.findall(r"<[^>]+>", value)
    desc_matches = re.findall(r"\[[^\]]+\]", value)

    # Hapus tags & deskripsi sementara dari kalimat
    tagless_value = value
    for tag in tag_matches:
        tagless_value = tagless_value.replace(tag, "")
    for desc in desc_matches:
        tagless_value = tagless_value.replace(desc, "")

    # Lindungi frasa penting
    protected_input, protected_map = protect_phrases(tagless_value.strip())

    # Terjemahkan bagian utama
    try:
        translated_main = translator.translate(protected_input)
    except Exception as e:
        print(f"❌ Gagal terjemahkan: {value} → {e}")
        return value

    translated_main = restore_protected_phrases(translated_main, protected_map)

    # Terjemahkan [deskripsi]
    translated_descs = []
    for desc in desc_matches:
        try:
            inner = desc[1:-1]
            protected, map_ = protect_phrases(inner)
            translated = translator.translate(protected)
            translated = restore_protected_phrases(translated, map_)
            translated_descs.append(f"[{translated}]")
        except Exception as e:
            print(f"❌ Gagal terjemahkan deskripsi: {desc} → {e}")
            translated_descs.append(desc)

    # Satukan hasil akhir
    result = "".join(tag_matches) + "".join(translated_descs)
    if translated_main:
        result += " " + translated_main

    return result.strip()

def process_line(line, line_number):
    match = re.match(r'(\s*)"([^"]+)"\s+"([^"]*)"', line)
    if match:
        indent, key, value = match.groups()
        if key != "Language":
            print(f"🔄 [{line_number}] Menerjemahkan '{key}': {value}")
            translated_value = translate_parts(value)
            print(f"✅  → {translated_value}\n")
            return f'{indent}"{key}" "{translated_value}"\n'
    return line

def translate_file(input_path, output_path):
    encoding = detect_encoding(input_path)
    print(f"📄 Encoding terdeteksi: {encoding}")

    with open(input_path, 'r', encoding=encoding) as infile, \
         open(output_path, 'w', encoding=encoding) as outfile:
        for i, line in enumerate(infile, 1):
            translated_line = process_line(line, i)
            outfile.write(translated_line)

    print("✅ Terjemahan selesai!")

if __name__ == "__main__":
    translate_file(input_file, output_file)
