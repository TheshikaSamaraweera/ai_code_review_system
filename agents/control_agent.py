from agents.quality_agent import run_quality_agent
from agents.static_analysis_agent import run_static_analysis
from agents.error_comparator_agent import compare_issues
from agents.critic_agent import run_critic_agent
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

    # Save code to temp file
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as temp_code_file:
        temp_code_file.write(code)
        temp_path = temp_code_file.name

    # Run Static Analysis
    static_results = run_static_analysis(temp_path)

    # Clean up
    os.remove(temp_path)

    # Compare Issues
    merged_issues = compare_issues(quality_results, static_results)

    # Critic Agent for reflection
    refined_issues = run_critic_agent(code, merged_issues, api_key)

    for issue in refined_issues:
        print(f"\n🔍 Refined [Line {issue['line']}]:")
        print(f"❗ {issue['description']}")
        print(f"💡 {issue['suggestion']}")
        print(f"ℹ️ {issue['explanation']}")

    print("\n✅ Phase 6 Complete: Refined suggestions with reasoning.")