import json
from llm.gemini_client import init_gemini
from memory.session_memory import remember_issue

def run_quality_agent(code, api_key, context=None):
    print("🔍 Running Quality Agent...")

    gemini = init_gemini()
    try:
        with open("prompts/quality_prompt.txt", "r") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        print("❌ Missing prompt file: prompts/quality_prompt.txt")
        return {"score": 0, "issues": []}

    context_str = json.dumps(context, indent=2) if context else "{}"
    prompt = f"{prompt_template}\n\nCODE:\n{code}\n\nCONTEXT:\n{context_str}"

    try:
        response = gemini.generate_content(prompt)
        json_str = response.text.strip().split("```json")[-1].split("```")[0].strip() if "```json" in response.text else response.text
        result = json.loads(json_str)
    except Exception as e:
        print("❌ Failed to parse Gemini response:", e)
        print("Raw output:\n", response.text)
        return {"score": 0, "issues": []}

    issues = result.get("issues", [])
    for issue in issues:
        issue.setdefault("explanation", "No specific explanation provided by the model.")
        issue.setdefault("severity", "medium")
        issue.setdefault("confidence", 0.9)
        issue.setdefault("priority", 0.8 if issue["severity"] == "high" else 0.6)
        remember_issue(issue)

    print(f"✅ Quality Agent completed - Score: {result.get('score', 0)}/100")
    return result