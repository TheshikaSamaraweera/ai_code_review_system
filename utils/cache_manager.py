import hashlib
import json
import os

def get_code_hash(code):
    return hashlib.sha256(code.encode('utf-8')).hexdigest()

def load_cached_results(code):
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    code_hash = get_code_hash(code)
    cache_file = os.path.join(cache_dir, f"{code_hash}.json")
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return None

def save_cached_results(code, results):
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    code_hash = get_code_hash(code)
    cache_file = os.path.join(cache_dir, f"{code_hash}.json")
    with open(cache_file, 'w') as f:
        json.dump(results, f)