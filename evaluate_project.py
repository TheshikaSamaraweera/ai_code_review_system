import os
import json
import difflib
from typing import List, Dict
from tabulate import tabulate
from agents.control_agent import EnhancedControlAgent, AnalysisConfig
from memory.session_memory import session_memory, show_session_summary
from utils.language_detector import detect_language
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def generate_synthetic_samples() -> List[Dict[str, any]]:
    samples = []

    # Sample 1: Security issue (eval injection)
    code1 = """
def unsafe_eval(input_str):
    result = eval(input_str)  # Injected issue: eval on user input
    return result

password = "hardcoded_secret"  # Injected issue: hardcoded secret
"""
    ground_truth1 = [
        {"line": 3, "description": "Use of eval() can lead to code injection", "severity": "critical"},
        {"line": 6, "description": "Hardcoded secrets detected", "severity": "high"},
        {"line": 6, "description": "Constant name 'password' doesn't conform to UPPER_CASE naming style",
         "severity": "low"}
    ]
    samples.append({"code": code1, "ground_truth": ground_truth1, "language": "Python"})

    # Sample 2: Code smell (long method, duplicate code)
    code2 = """
def long_method(x):
    # Over 50 lines (simulated with repetition)
    print(x)
    print(x)  # Duplicate
    print(x)  # Duplicate
    if x > 0:
        for i in range(100):  # High complexity
            print(i)
    # ... (imagine more lines)
"""
    ground_truth2 = [
        {"line": 2, "description": "Long Method", "severity": "medium"},
        {"line": 2, "description": "Missing docstring for the function `long_method`", "severity": "low"},
        {"line": 4, "description": "Duplicate Code", "severity": "medium"},
        {"line": 7, "description": "High Complexity", "severity": "high"}
    ]
    samples.append({"code": code2, "ground_truth": ground_truth2, "language": "Python"})

    # Sample 3: Quality issue (no docstrings, magic numbers)
    code3 = """
def add_numbers(a, b):
    return a + b + 42  # Magic number
"""
    ground_truth3 = [
        {"line": 2, "description": "Missing docstring or explanation", "severity": "low"},
        {"line": 3, "description": "Magic number 42 found", "severity": "low"}
    ]
    samples.append({"code": code3, "ground_truth": ground_truth3, "language": "Python"})

    # Sample 4: No issues (clean code)
    code4 = """
def safe_add(a: int, b: int) -> int:
    \"\"\"Adds two numbers safely.\"\"\"
    return a + b
"""
    ground_truth4 = []
    samples.append({"code": code4, "ground_truth": ground_truth4, "language": "Python"})

    # Sample 5: Mixed (security + smell)
    code5 = """
import os

def run_command(cmd):
    os.system(cmd)  # Command injection
    # Duplicate code block
    print("Duplicate")
    print("Duplicate")
"""
    ground_truth5 = [
        {"line": 5, "description": "os.system() is vulnerable to command injection", "severity": "high"},
        {"line": 7, "description": "Duplicate Code", "severity": "medium"}
    ]
    samples.append({"code": code5, "ground_truth": ground_truth5, "language": "Python"})

    return samples


def normalize_description(desc: str) -> str:
    """Normalize description by removing punctuation and converting to lowercase."""
    desc = desc.lower().strip().replace("`", "").replace("'", "").replace("(", "").replace(")", "").replace(".", "")
    return desc


def is_match(detected: Dict, ground: Dict, similarity_threshold: float = 0.25) -> bool:
    # Line match: exact or ±2
    line_diff = abs(detected.get("line", 0) - ground.get("line", 0))
    if line_diff > 2:
        print(f"Debug: Line mismatch (diff={line_diff}): detected={detected.get('line')}, ground={ground.get('line')}")
        return False

    # Severity adjustment: allow mismatch if descriptions match strongly
    detected_severity = detected.get("severity", "medium").lower()
    ground_severity = ground.get("severity", "medium").lower()
    severity_weight = 0.1 if detected_severity == ground_severity else 0.05

    # Keyword-based matching with weights
    keywords = {
        "eval": 0.4, "injection": 0.3, "code": 0.2,
        "hardcoded": 0.4, "secret": 0.3, "password": 0.2,
        "long": 0.4, "method": 0.3, "duplicate": 0.4,
        "complexity": 0.4, "nesting": 0.2, "loop": 0.2,
        "docstring": 0.5, "missing": 0.4, "explanation": 0.3,
        "magic": 0.4, "number": 0.3,
        "os.system": 0.4, "command": 0.3,
        "naming": 0.3, "convention": 0.2, "style": 0.2
    }
    desc1 = normalize_description(detected.get("description", ""))
    desc2 = normalize_description(ground.get("description", ""))
    score = 0
    for keyword, weight in keywords.items():
        if keyword in desc1 and keyword in desc2:
            score += weight
    score += severity_weight
    print(f"Debug: Similarity for '{detected.get('description')}' vs '{ground.get('description')}': {score:.2f}")
    return score >= similarity_threshold


def compute_metrics(detected_issues: List[Dict], ground_truth: List[Dict]) -> Dict:
    tp = 0
    matched_ground = set()
    unmatched_detected = []
    unmatched_ground = list(range(len(ground_truth)))

    for det in detected_issues:
        matched = False
        for i, gt in enumerate(ground_truth):
            if i not in matched_ground and is_match(det, gt):
                tp += 1
                matched_ground.add(i)
                unmatched_ground.remove(i)
                matched = True
                break
        if not matched:
            unmatched_detected.append(det)

    fp = len(detected_issues) - tp
    fn = len(ground_truth) - tp

    precision = tp / (tp + fp) if (tp + fp) > 0 else 1
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "unmatched_detected": unmatched_detected,
        "unmatched_ground": [ground_truth[i] for i in unmatched_ground]
    }


def deduplicate_issues(issues: List[Dict]) -> List[Dict]:
    """Deduplicate issues based on line, description, and severity."""
    seen = set()
    deduplicated = []
    for issue in issues:
        key = (issue.get("line"), normalize_description(issue.get("description", "")), issue.get("severity", "medium"))
        if key not in seen:
            seen.add(key)
            deduplicated.append(issue)
    return deduplicated


def run_analysis_on_sample(code: str, language: str, project_dir: str) -> List[Dict]:
    try:
        config = AnalysisConfig(interactive_mode=False)
        agent = EnhancedControlAgent(config)
        results = agent.analyze_code_comprehensive(code, language, project_dir)

        # Debug: Print analysis_summary structure
        print("Debug: analysis_summary structure:", json.dumps(results.analysis_summary, indent=2, default=str))

        # Extract issues from refined_issues
        detected_issues = results.analysis_summary.get('refined_issues', [])
        if not detected_issues:
            print("Warning: No refined_issues found")
            detected_issues = []

        # Deduplicate issues
        detected_issues = deduplicate_issues(detected_issues)

        # Store issues for this sample only
        session_memory["issues"] = detected_issues
        print("Debug: Detected issues:", json.dumps(detected_issues, indent=2))
        return detected_issues
    except Exception as e:
        print(f"Error analyzing sample: {e}")
        return []


def generate_metrics_table(metrics_list: List[Dict]) -> str:
    headers = ["Sample", "TP", "FP", "FN", "Precision", "Recall", "F1 Score"]
    table_data = []
    for i, metrics in enumerate(metrics_list, 1):
        table_data.append([
            f"Sample {i}",
            metrics["tp"],
            metrics["fp"],
            metrics["fn"],
            f"{metrics['precision']:.2f}",
            f"{metrics['recall']:.2f}",
            f"{metrics['f1']:.2f}"
        ])

    # Add aggregate row
    if metrics_list:
        avg_precision = sum(m["precision"] for m in metrics_list) / len(metrics_list)
        avg_recall = sum(m["recall"] for m in metrics_list) / len(metrics_list)
        avg_f1 = sum(m["f1"] for m in metrics_list) / len(metrics_list)
        table_data.append([
            "Aggregate",
            sum(m["tp"] for m in metrics_list),
            sum(m["fp"] for m in metrics_list),
            sum(m["fn"] for m in metrics_list),
            f"{avg_precision:.2f}",
            f"{avg_recall:.2f}",
            f"{avg_f1:.2f}"
        ])

    table = tabulate(table_data, headers=headers, tablefmt="grid")

    # Generate Chart.js bar chart
    chart_data = {
        "type": "bar",
        "data": {
            "labels": [f"Sample {i}" for i in range(1, len(metrics_list) + 1)] + ["Aggregate"],
            "datasets": [
                {
                    "label": "Precision",
                    "data": [m["precision"] for m in metrics_list] + [avg_precision],
                    "backgroundColor": "rgba(75, 192, 192, 0.7)",
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "borderWidth": 1
                },
                {
                    "label": "Recall",
                    "data": [m["recall"] for m in metrics_list] + [avg_recall],
                    "backgroundColor": "rgba(255, 99, 132, 0.7)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 1
                },
                {
                    "label": "F1 Score",
                    "data": [m["f1"] for m in metrics_list] + [avg_f1],
                    "backgroundColor": "rgba(54, 162, 235, 0.7)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 1
                }
            ]
        },
        "options": {
            "scales": {
                "y": {
                    "beginAtZero": True,
                    "max": 1,
                    "title": {"display": True, "text": "Score"}
                },
                "x": {
                    "title": {"display": True, "text": "Sample"}
                }
            },
            "plugins": {
                "legend": {"position": "top"},
                "title": {"display": True, "text": "Evaluation Metrics per Sample"}
            }
        }
    }

    print("\nMetrics Table:")
    print(table)
    print("\nChart (visualize in a compatible UI):")
    print("```chartjs")
    print(json.dumps(chart_data, indent=2))
    print("```")
    return table


def main():
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY environment variable not set.")
        return

    print("Generating synthetic samples...")
    samples = generate_synthetic_samples()
    all_metrics = []

    print("\nRunning analysis on samples...")
    for i, sample in enumerate(samples, 1):
        print(f"\nEvaluating Sample {i}...")
        # Clear session_memory["issues"] for each sample
        session_memory["issues"] = []
        project_dir = os.path.dirname(__file__)
        try:
            detected_issues = run_analysis_on_sample(sample["code"], sample["language"], project_dir)
            metrics = compute_metrics(detected_issues, sample["ground_truth"])
            all_metrics.append(metrics)
            print(f"Sample {i} Metrics:")
            print(json.dumps(metrics, indent=2))
            if metrics["unmatched_detected"] or metrics["unmatched_ground"]:
                print("Unmatched Issues:")
                print("Detected but not in ground truth:", json.dumps(metrics["unmatched_detected"], indent=2))
                print("Ground truth not detected:", json.dumps(metrics["unmatched_ground"], indent=2))
        except Exception as e:
            print(f"Failed to analyze Sample {i}: {e}")
            all_metrics.append({
                "tp": 0,
                "fp": 0,
                "fn": len(sample["ground_truth"]),
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "unmatched_detected": [],
                "unmatched_ground": sample["ground_truth"]
            })

    print("\nMetrics Table:")
    print(generate_metrics_table(all_metrics))

    print("\nSession Summary:")
    show_session_summary()


if __name__ == "__main__":
    main()