import os
import json
import toml
import yaml
from utils.language_detector import detect_language

def analyze_project_context(project_dir):
    context = {
        "language": None,
        "frameworks": [],
        "conventions": {},
        "dependencies": []
    }

    # Detect language from files
    for file in os.listdir(project_dir):
        if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.rb', '.php', '.go', '.rs', '.kt', '.swift')):
            context["language"] = detect_language(file)

    # Parse configuration files
    if os.path.exists(os.path.join(project_dir, ".eslintrc.json")):
        with open(os.path.join(project_dir, ".eslintrc.json"), 'r') as f:
            eslint_config = json.load(f)
            context["conventions"]["eslint"] = eslint_config.get("rules", {})
            context["frameworks"].append("JavaScript")

    if os.path.exists(os.path.join(project_dir, "requirements.txt")):
        with open(os.path.join(project_dir, "requirements.txt"), 'r') as f:
            context["dependencies"] = [line.strip() for line in f if line.strip()]
            context["frameworks"].append("Python")

    if os.path.exists(os.path.join(project_dir, "pyproject.toml")):
        with open(os.path.join(project_dir, "pyproject.toml"), 'r') as f:
            pyproject = toml.load(f)
            context["conventions"]["black"] = pyproject.get("tool", {}).get("black", {})
            context["frameworks"].append("Python")

    return context