import subprocess
import json
import tempfile
import os
from utils.language_detector import detect_language
from utils.cache_manager import load_cached_results, save_cached_results

def run_static_analysis(file_path):
    print("🔎 Running Static Analysis...")
    language = detect_language(file_path)
    code = open(file_path, 'r').read()

    # Check cache
    cached_results = load_cached_results(code)
    if cached_results:
        print(f"✅ Using cached static analysis results - Found {len(cached_results)} issues")
        return cached_results

    all_issues = []
    extension = os.path.splitext(file_path)[1] or '.py'
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False, mode="w") as temp_file:
        temp_file.write(code)
        temp_path = temp_file.name

    if language == "Python":
        all_issues += run_pylint(temp_path)
        all_issues += run_bandit(temp_path)
    elif language == "JavaScript" or language == "TypeScript":
        all_issues += run_eslint(temp_path)
    elif language == "Java":
        all_issues += run_checkstyle(temp_path)

    os.remove(temp_path)
    save_cached_results(code, all_issues)
    print(f"✅ Static Analysis completed - Found {len(all_issues)} issues")
    return all_issues

def run_pylint(file_path):
    issues = []
    try:
        result = subprocess.run(
            ["pylint", file_path, "-f", "json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10
        )
        data = json.loads(result.stdout)
        for item in data:
            issues.append({
                "tool": "pylint",
                "line": item.get("line", 0),
                "issue": item.get("message", ""),
                "suggestion": item.get("symbol", ""),
                "severity": "medium",
                "confidence": 0.8
            })
    except Exception as e:
        print(f"⚠️ pylint failed: {e}")
    return issues

def run_bandit(file_path):
    issues = []
    try:
        result = subprocess.run(
            ["bandit", "-f", "json", "-q", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10
        )
        data = json.loads(result.stdout)
        for item in data["results"]:
            issues.append({
                "tool": "bandit",
                "line": item.get("line_number", 0),
                "issue": item.get("issue_text", ""),
                "suggestion": item.get("test_name", ""),
                "severity": "high",
                "confidence": 0.95
            })
    except Exception as e:
        print(f"⚠️ bandit failed: {e}")
    return issues

def run_eslint(file_path):
    issues = []
    try:
        result = subprocess.run(
            ["eslint", file_path, "--format", "json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10
        )
        data = json.loads(result.stdout)
        for file in data:
            for item in file.get("messages", []):
                issues.append({
                    "tool": "eslint",
                    "line": item.get("line", 0),
                    "issue": item.get("message", ""),
                    "suggestion": item.get("ruleId", ""),
                    "severity": "medium",
                    "confidence": 0.85
                })
    except Exception as e:
        print(f"⚠️ eslint failed: {e}")
    return issues

def run_checkstyle(file_path):
    issues = []
    try:
        result = subprocess.run(
            ["checkstyle", "-c", "/sun_checks.xml", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10
        )
        lines = result.stdout.splitlines()
        for line in lines:
            if "ERROR" in line:
                parts = line.split(":")
                if len(parts) > 2:
                    issues.append({
                        "tool": "checkstyle",
                        "line": int(parts[1]) if parts[1].isdigit() else 0,
                        "issue": parts[-1].strip(),
                        "suggestion": "Follow Java style guidelines",
                        "severity": "medium",
                        "confidence": 0.8
                    })
    except Exception as e:
        print(f"⚠️ checkstyle failed: {e}")
    return issues