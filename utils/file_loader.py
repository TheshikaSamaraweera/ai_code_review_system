import os


def load_file(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found.")

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
