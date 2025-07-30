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
    print("🧩 Activating Agents...\n")

    # Replace QualityAgent stub with real call
    from os import getenv
    api_key = "AIzaSyDaW3FIrAlu3Kf_iLIDt8j5wlOw3lXTDiY"
    if not api_key:
        print("❌ GEMINI_API_KEY not set in environment.")
        return

    print("🧩 Activating Agents...\n")

    # Run Quality Agent (LLM)
    quality_results = run_quality_agent(code, api_key)

    # Phase 2: Static Analysis (write to temp file)
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as temp_code_file:
            temp_code_file.write(code)
            temp_path = temp_code_file.name

        static_results = run_static_analysis(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # Phase 3: Compare
    merged_issues = compare_issues(quality_results, static_results)

    # Phase 4–6: Critic
    refined_issues = run_critic_agent(code, merged_issues, api_key)
    # Run Optimization Agent
    optimization_issues = run_optimization_agent(code, api_key)
    if optimization_issues:
        for issue in refined_issues:
            print(f"\n🔍 Refined [Line {issue['line']}]:")
            print(f"❗ {issue['description']}")
            print(f"💡 {issue['suggestion']}")
            print(f"ℹ️ {issue['explanation']}")
            remember_issue(issue)

    print("\n✅ Phase 6 Complete: Refined suggestions with reasoning.")

    # Phase 7: Refactor
    refactored_code = run_refactor_agent(code, refined_issues, api_key)
    if not refactored_code:
        return

    show_code_diff(code, refactored_code)
    print("\n✅ Phase 7 Complete: Refactored code generated and compared.")
    # ... after show_code_diff()
    apply_fixes(code, refactored_code)
    # Optionally return for Phase 8
    show_session_summary()
    return refactored_code
