import os
import tempfile
from utils.file_loader import load_file  # optional if you're using a loader
from agents.quality_agent import run_quality_agent
from agents.static_analysis_agent import run_static_analysis
from agents.error_comparator_agent import compare_issues
from controls.recursive_controller import build_langgraph_loop


def main():
    # Load API key
    api_key = "AIzaSyDaW3FIrAlu3Kf_iLIDt8j5wlOw3lXTDiY"
    # Load code file
    code_path = input("📄 Enter the path to your Python code (e.g., sample_code.py): ").strip()
    if not os.path.exists(code_path):
        print("❌ File not found.")
        return

    with open(code_path, "r") as f:
        code = f.read()

    print("\n🔍 Phase 1: Running Initial Analysis...")

    # Run Quality Agent
    quality_results = run_quality_agent(code, api_key)
    score = quality_results.get("score", 0)

    # Run Static Analysis
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as temp_file:
        temp_file.write(code)
        temp_path = temp_file.name
    static_results = run_static_analysis(temp_path)
    os.remove(temp_path)

    # Merge AI and static tool issues
    merged_issues = compare_issues(quality_results, static_results)

    print("\n📌 Merged Issues Summary:")
    for i, issue in enumerate(merged_issues, 1):
        print(f"{i}. Line {issue['line']} | {issue['description']} ➜ {issue['suggestion']}")

    print(f"\n📊 Initial Quality Score: {score}")

    # Ask if user wants to apply fixes and enter iterative optimization
    answer = input("\n🤖 Apply fixes and optimize code iteratively? (y/N): ").strip().lower()
    if answer != "y":
        print("\n🚫 Exiting after initial review. No changes applied.")
        return

    print("\n♻️ Entering Iterative Optimization Mode...\n")

    # Initialize LangGraph loop state
    state = {
        "api_key": api_key,
        "code": code,
        "iteration": 0,
        "continue_": True,
        "auto_refine": True,
        "max_outer_iterations": 4,
        "history": [],
        "best_code": code,
        "best_score": score,
        "score": score,
        "no_improvement_count": 0,
        "best_refined_issues": []
    }

    graph = build_langgraph_loop()
    final = graph.invoke(state)

    # Final output
    best_code = final.get("best_code", "[No final code]")
    print("\n✅ Final Refactored Code:\n")
    print(best_code)

    print("\n📚 Iteration Summary:")
    for step in final.get("history", []):
        print(f"\n🧾 Iteration {step['iteration']}:")
        print(f"   Score: {step.get('score', 'N/A')}")
        print(f"   Issues: {len(step['refined_issues'])}")
        print(f"   Code Preview:\n{step['refactored_code'][:200]}...")

if __name__ == "__main__":
    main()
