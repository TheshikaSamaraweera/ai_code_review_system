import json
from llm.gemini_client import init_gemini

def run_quality_agent(code, api_key):
    print("\n🔍 Running QualityAgent...")

    gemini = init_gemini(api_key)

    with open("prompts/quality_prompt.txt", "r") as f:
        prompt_template = f.read()

    prompt = f"{prompt_template}\n\nCODE:\n{code}"

    response = gemini.generate_content(prompt)

    try:
        json_str = response.text.strip().split("```json")[-1].split("```")[0].strip() \
            if "```json" in response.text else response.text
        result = json.loads(json_str)
    except Exception as e:
        print("❌ Failed to parse Gemini response:", e)
        print("Raw output:\n", response.text)
        return {}
    
    print(f"✅ Total Quality Issues Found: {len(result.get('issues', []))}")

    print(f"✅ Quality Agent Score: {result.get('score')}")
    # Inside for loop where issues are appended
    for issue in result.get("issues", []):
        print(f"⚠️ Line {issue['line']}: {issue['issue']} ➜ {issue['suggestion']}")

        # Add severity and confidence estimation (mock logic)
        issue["severity"] = "high" if "security" in issue["issue"].lower() else "medium"
        issue["confidence"] = 0.9  # Default for LLM suggestions

    return result
