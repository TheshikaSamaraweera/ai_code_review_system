import json
from llm.gemini_client import init_gemini
from memory.session_memory import remember_issue  # Optional: for Phase 9 session tracking

def run_critic_agent(code, merged_issues, api_key):
    print("\n🤔 Critic Agent Activated: Reflecting on all issues...")

    gemini = init_gemini()

    # Load structured prompt
    try:
        with open("prompts/critic_prompt.txt", "r") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        print("❌ Missing prompt: prompts/critic_prompt.txt")
        return merged_issues

    # Merge into full prompt
    issue_summary = json.dumps(merged_issues, indent=2)
    prompt = f"{prompt_template}\n\nSOURCE CODE:\n{code}\n\nISSUES:\n{issue_summary}"

    try:
        response = gemini.generate_content(prompt)
    except Exception as e:
        print("❌ Gemini call failed:", e)
        return merged_issues

    # Extract and parse JSON from response
    try:
        raw_output = response.text.strip()
        json_str = raw_output.split("```json")[-1].split("```")[0].strip() if "```json" in raw_output else raw_output
        result = json.loads(json_str)
        refined_issues = result.get("improved_issues", [])
    except Exception as e:
        print("❌ Failed to parse Critic Agent response:", e)
        print("📝 Raw output:\n", response.text)
        return merged_issues

    if not refined_issues:
        print("⚠️ Critic Agent returned no refined issues. Using original set.")
        return merged_issues

    # Optionally remember refined issues
    for issue in refined_issues:
        remember_issue(issue)
        issue.setdefault("severity", "medium")
        issue.setdefault("confidence", 0.85)

    print(f"✅ Critic Agent provided {len(refined_issues)} refined issues.")
    return refined_issues
