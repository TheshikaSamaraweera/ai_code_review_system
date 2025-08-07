import json
from llm.gemini_client import init_gemini
from memory.session_memory import remember_issue

def run_critic_agent(code, merged_issues, api_key):
    print("\n🤔 Critic Agent Activated: Reflecting on all issues...")

    gemini = init_gemini()
    try:
        with open("prompts/critic_prompt.txt", "r") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        print("❌ Missing prompt: prompts/critic_prompt.txt")
        return merged_issues

    issue_summary = json.dumps(merged_issues, indent=2)
    prompt = f"{prompt_template}\n\nSOURCE CODE:\n{code}\n\nISSUES:\n{issue_summary}"

    try:
        response = gemini.generate_content(prompt)
        json_str = response.text.strip().split("```json")[-1].split("```")[0].strip() if "```json" in response.text else response.text
        result = json.loads(json_str)
        refined_issues = result.get("improved_issues", [])
    except Exception as e:
        print("❌ Failed to parse Critic Agent response:", e)
        print("📝 Raw output:\n", response.text)
        return merged_issues

    if not refined_issues:
        print("⚠️ Critic Agent returned no refined issues. Using original set.")
        return merged_issues

    for issue in refined_issues:
        issue.setdefault("explanation", "No specific explanation provided by the model.")
        issue.setdefault("severity", "medium")
        issue.setdefault("confidence", 0.85)
        issue.setdefault("priority", 0.8 if issue["severity"] == "high" else 0.6)
        remember_issue(issue)

    print(f"✅ Critic Agent provided {len(refined_issues)} refined issues.")
    return refined_issues