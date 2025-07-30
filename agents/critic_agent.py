import json
from llm.gemini_client import init_gemini

def run_critic_agent(code, merged_issues, api_key):
    print("\n🧐 Running Critic Agent...")

    gemini = init_gemini(api_key)

    with open("prompts/critic_prompt.txt", "r") as f:
        prompt_template = f.read()

    # Format merged issues for prompt
    issue_summary = json.dumps(merged_issues, indent=2)
    prompt = f"{prompt_template}\n\nSOURCE CODE:\n{code}\n\nISSUES:\n{issue_summary}"

    response = gemini.generate_content(prompt)

    try:
        json_str = response.text.strip().split("```json")[-1].split("```")[0].strip() \
            if "```json" in response.text else response.text
        result = json.loads(json_str)
    except Exception as e:
        print("❌ Failed to parse critic response:", e)
        print("Raw output:\n", response.text)
        return []

    print(f"✅ Critic Agent provided {len(result.get('improved_issues', []))} refined issues.")
    return result.get("improved_issues", [])
