import json
from llm.gemini_client import init_gemini

def run_security_agent(code, api_key):
    print("\n🔍 Running Security Agent...")

    gemini = init_gemini(api_key)

    try:
        with open("prompts/security_prompt.txt", "r") as f:
            prompt_template = f.read()

    except FileNotFoundError:
        print("❌ Missing prompt file: prompts/security_prompt.txt")
        return []

    prompt = f"{prompt_template}\n\nSOURCE CODE:\n{code}"

    try:
        response = gemini.generate_content(prompt)
    except Exception as e:
        print("❌ Gemini API call failed:", e)
        return {}

    try:
        raw_output = response.text.strip()
        json_str = raw_output.split("```json")[-1].split("```")[0].strip() if "```json" in raw_output else raw_output
        result = json.loads(json_str)
    except Exception as e:
        print("❌ Failed to parse Security Agent output:", e)
        print("📝 Raw output:\n", response.text)
        return {}

    # Show results
    print(f"✅ Total Security Issues Found: {len(result.get('issues', []))}")

    for issue in result.get("issues", []):
        print(f"🔴 Line {issue['line']}: {issue['issue']} ➜ {issue['suggestion']}")
        issue["severity"] = "high"  if "security" in issue["issue"].lower() else "medium"
        issue["confidence"] = 0.9  # Default confidence for LLM suggestions
    return result