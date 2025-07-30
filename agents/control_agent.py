import os
import tempfile

from agents.quality_agent import run_quality_agent
from agents.static_analysis_agent import run_static_analysis

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

    # Run Quality Agent
    quality_results = run_quality_agent(code, api_key)

    # Write code to temp file for static tools
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as temp_code_file:
        temp_code_file.write(code)
        temp_path = temp_code_file.name

    # Run Static Analysis Agent
    static_results = run_static_analysis(temp_path)

    # Clean up
    os.remove(temp_path)

    print("\n📊 Summary:")
    print(f"🔍 Quality Score: {quality_results.get('score')}")
    print(f"📋 Static Issues: {len(static_results)}")
