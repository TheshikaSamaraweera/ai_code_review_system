from agents.quality_agent import run_quality_agent

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

    quality_results = run_quality_agent(code, api_key)

    print("\n✅ Completed QualityAgent")
    print("🧪 (Other agents are still stubs)")
