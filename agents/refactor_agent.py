# refactor_agent.py
import json
from llm.gemini_client import init_gemini

def run_refactor_agent(original_code, refined_issues, api_key):
    print("\n🔧 Running Refactor Agent...")

    gemini = init_gemini(api_key)

    with open("prompts/refactor_prompt.txt", "r") as f:
        prompt_template = f.read()

    refined_str = json.dumps(refined_issues, indent=2)
    full_prompt = f"{prompt_template}\n\nsource_code:\n{original_code}\n\nrefined_issues:\n{refined_str}"

    response = gemini.generate_content(full_prompt)

    try:
        code_block = response.text.strip().split("```python")[-1].split("```")[0].strip()
    except Exception as e:
        print("❌ Failed to extract refactored code:", e)
        print("Raw output:\n", response.text)
        return None

    print("✅ Refactor Agent completed.")
    return code_block
