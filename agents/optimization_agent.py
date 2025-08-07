import json
from llm.gemini_client import init_gemini

def run_optimization_agent(code, api_key):
    print("\n🚀 Optimization Agent Running...")

    gemini = init_gemini()

    try:
        with open("prompts/optimization_prompt.txt", "r") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        print("❌ Missing prompt file: prompts/optimization_prompt.txt")
        return []

    prompt = f"{prompt_template}\n\nSOURCE CODE:\n{code}"

    try:
        response = gemini.generate_content(prompt)
    except Exception as e:
        print("❌ Gemini API call failed:", e)
        return []

    try:
        raw_output = response.text.strip()
        json_str = raw_output.split("```json")[-1].split("```")[0].strip() if "```json" in raw_output else raw_output
        result = json.loads(json_str)
    except Exception as e:
        print("❌ Failed to parse Optimization Agent output:", e)
        print("📝 Raw output:\n", response.text)
        return []

    print(f"✅ Optimization Agent returned {len(result)} suggestions.")
    return result
