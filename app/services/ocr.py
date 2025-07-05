import easyocr

def initialize_ocr():
    # Suporte a português e inglês
    return easyocr.Reader(['pt', 'en'])

def read_text(reader, file_path):
    results = reader.readtext(file_path)
    return ' '.join([result[1] for result in results])
