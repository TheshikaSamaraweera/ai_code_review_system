from agents.quality_agent import run_quality_agent
from agents.static_analysis_agent import run_static_analysis
from agents.error_comparator_agent import compare_issues
from agents.critic_agent import run_critic_agent
from agents.refactor_agent import run_refactor_agent
from utils.code_diff import show_code_diff
from cli.apply_fixes import apply_fixes
from memory.session_memory import remember_issue, remember_feedback, show_session_summary
from agents.optimization_agent import run_optimization_agent
from utils.language_detector import detect_language
from utils.context_analyzer import analyze_project_context
import tempfile
import os

def run_control_agent(code, language, project_dir="."):
    print("\n🧠 Control Agent Activated")
    print(f"➡️ Language: {language}")
    print("🧩 Phase 1: Analyze Only...\n")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set.")
        return

    context = analyze_project_context(project_dir)
    print(f"📋 Project Context: {context}")

    quality_results = run_quality_agent(code, api_key, context)

    with tempfile.NamedTemporaryFile(suffix=f".{language.lower()}", delete=False, mode="w") as temp_code_file:
        temp_code_file.write(code)
        temp_path = temp_code_file.name
    static_results = run_static_analysis(temp_path)
    os.remove(temp_path)

    merged_issues = compare_issues(quality_results, static_results)
    refined_issues = run_critic_agent(code, merged_issues, api_key)

    print("\n🧾 Final Suggestions (Phase 1):\n")
    for issue in refined_issues:
        print(f"🔍 Line {issue['line']} | {issue['description']}")
        print(f"💡 Suggestion: {issue['suggestion']}")
        print(f"ℹ️ Explanation: {issue.get('explanation', 'N/A')}")
        print(f"🔴 Severity: {issue.get('severity')} | 🔘 Confidence: {issue.get('confidence')}\n")

    user_input = input("🤖 Do you want to apply and iteratively refine the code? (y/N): ").strip().lower()
    if user_input != "y":
        print("🚫 Skipping iterative refinement.")
        return

    print("\n🔁 Starting AI-Driven Refinement Loop...")
    refactored_code = run_refactor_agent(code, refined_issues, api_key)
    feedback = apply_fixes(code, refactored_code, refined_issues)

    from controls.recursive_controller import build_langgraph_loop
    graph = build_langgraph_loop()

    state = {
        "api_key": api_key,
        "code": refactored_code if refactored_code else code,
        "iteration": 0,
        "continue_": True,
        "best_code": code,
        "best_score": quality_results.get("score", 0),
        "best_issues": refined_issues,
        "issue_count": len(refined_issues),
        "issues_fixed": 0,
        "feedback": feedback,
        "min_score_threshold": 95.0,
        "max_high_severity_issues": 0,
        "max_iterations": 5,
        "context": context,
        "optimization_applied": False
    }

    final = graph.invoke(state)
    best_code = final.get("best_code", code)
    print("\n✅ Final Refactored Code:\n")
    print(best_code)

    print("\n📚 Iteration Summary:")
    for step in final.get("history", []):
        print(f"\n🧾 Iteration {step['iteration']}:")
        print(f"   Score: {step['score']}")
        print(f"   Issues Remaining: {step['issue_count']}")
        print(f"   Issues Fixed: {step['issues_fixed']}")
        print(f"   Preview:\n{step['refactored_code']}\n")

    return best_code