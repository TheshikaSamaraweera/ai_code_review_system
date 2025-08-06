import json
from llm.gemini_client import init_gemini


def run_quality_agent(code, api_key, context=None):
    print("🔍 Running Quality Agent...")

    gemini = init_gemini()
    with open("prompts/quality_prompt.txt", "r") as f:
        prompt_template = f.read()

    context_str = json.dumps(context, indent=2) if context else "{}"
    prompt = f"{prompt_template}\n\nCODE:\n{code}\n\nCONTEXT:\n{context_str}"

    response = gemini.generate_content(prompt)

    try:
        json_str = response.text.strip().split("```json")[-1].split("```")[
            0].strip() if "```json" in response.text else response.text
        result = json.loads(json_str)
    except Exception as e:
        print("❌ Failed to parse Gemini response:", e)
        print("Raw output:\n", response.text)
        return {}

    print(f"✅ Quality Agent completed - Score: {result.get('score')}/100")

    for issue in result.get("issues", []):
        issue["severity"] = "high" if "security" in issue["issue"].lower() else "medium"
        issue["confidence"] = 0.9

    return result