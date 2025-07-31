from agents.quality_agent import run_quality_agent
from agents.static_analysis_agent import run_static_analysis
from agents.error_comparator_agent import compare_issues
from agents.critic_agent import run_critic_agent
from agents.refactor_agent import run_refactor_agent
from utils.code_diff import show_code_diff
from cli.apply_fixes import apply_fixes
from memory.session_memory import remember_issue, remember_feedback, show_session_summary
from agents.optimization_agent import run_optimization_agent
import tempfile
import os

def run_control_agent(code, language):
    print("\n🧠 Control Agent Activated")
    print(f"➡️ Language: {language}")
    print("🧩 Phase 1: Analyze Only...\n")

    # Replace QualityAgent stub with real call
    from os import getenv
    api_key = "AIzaSyDaW3FIrAlu3Kf_iLIDt8j5wlOw3lXTDiY"
    if not api_key:
        print("❌ No API key provided.")
        return

    # Run Quality Agent
    quality_results = run_quality_agent(code, api_key)

    # Static Analysis
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as temp_code_file:
        temp_code_file.write(code)
        temp_path = temp_code_file.name
    static_results = run_static_analysis(temp_path)
    os.remove(temp_path)

    # Merge
    merged_issues = compare_issues(quality_results, static_results)

    # Refine via critic
    refined_issues = run_critic_agent(code, merged_issues, api_key)

    print("\n🧾 Final Suggestions (Phase 1):\n")
    for issue in refined_issues:
        print(f"🔍 Line {issue['line']} | {issue['description']}")
        print(f"💡 Suggestion: {issue['suggestion']}")
        print(f"ℹ️ Explanation: {issue.get('explanation', 'N/A')}")
        print(f"🔴 Severity: {issue.get('severity')} | 🔘 Confidence: {issue.get('confidence')}\n")

    # Ask user
    user_input = input("🤖 Do you want to apply and iteratively refine the code? (y/N): ").strip().lower()
    if user_input != "y":
        print("🚫 Skipping iterative refinement.")
        return

    print("\n🔁 Starting AI-Driven Refinement Loop...")

    from controls.recursive_controller import build_langgraph_loop
    graph = build_langgraph_loop()

    state = {
        "api_key": api_key,
        "code": code,
        "iteration": 0,
        "continue_": True,
        "auto_refine": True,
        "max_outer_iterations": 4,
    }

    final = graph.invoke(state)

    # Show final result
    best_code = final.get("best_code", code)
    print("\n✅ Final Refactored Code:\n")
    print(best_code)

    print("\n📚 Iteration Summary:")
    for step in final.get("history", []):
        print(f"\n🧾 Iteration {step['iteration']}:")
        print(f"   Score: {step['score']}")
        print(f"   Issues: {len(step['refined_issues'])}")
        print(f"   Preview:\n{step['refactored_code'][:200]}...\n")

    return best_code
