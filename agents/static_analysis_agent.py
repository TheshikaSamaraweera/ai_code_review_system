import subprocess
import json
import tempfile
import os

def run_static_analysis(file_path):
    print("\n🔎 Running Static Analysis Agent...")

    all_issues = []

    all_issues += run_pylint(file_path)
    all_issues += run_bandit(file_path)
    # Optional: all_issues += run_semgrep(file_path)

    print(f"✅ Static Analysis found {len(all_issues)} issues.")
    for issue in all_issues:
        print(f"🟡 Line {issue['line']}: {issue['issue']} ➜ {issue['suggestion']}")
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
