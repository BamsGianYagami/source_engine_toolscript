# convert_encoding.py

input_file = "closecaption_indonesian_python.txt"  # ganti dengan file hasil terjemahanmu
output_file = "closecaption_indonesian.txt"  # output final

with open(input_file, 'r', encoding='utf-8') as infile:
    content = infile.read()

with open(output_file, 'w', encoding='utf-16') as outfile:
    outfile.write(content)

print("✅ File berhasil dikonversi ke UTF-16 dan siap dipakai di game.")
