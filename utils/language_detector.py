import os

def detect_language(file_path):
    extension_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.go': 'Go',
        '.rs': 'Rust',
        '.kt': 'Kotlin',
        '.swift': 'Swift'
    }

    for ext, lang in extension_map.items():
        if file_path.endswith(ext):
            return lang
    return "Unknown"