from memory.session_memory import remember_feedback


def apply_fixes(original_code, refactored_code, refined_issues):
    print("\n💬 Review and apply suggested fixes:")
    feedback = []

    for i, issue in enumerate(refined_issues, 1):
        print(f"\n{i}. Line {issue['line']}: {issue['description']}")
        print(f"   Suggestion: {issue['suggestion']}")
        print(f"   Explanation: {issue.get('explanation', 'N/A')}")
        user_input = input(f"   Apply this fix? (y/N): ").strip().lower()
        accepted = user_input == "y"
        feedback.append({
            "line": issue["line"],
            "description": issue["description"],
            "accepted": accepted
        })
        remember_feedback(issue["line"], issue["description"], accepted)

    apply_all = input("\n💾 Apply all accepted fixes and save? (y/N): ").strip().lower()
    if apply_all == "y":
        filename = input("Enter filename to save (e.g., fixed_code.py): ").strip()
        try:
            with open(filename, "w") as f:
                f.write(refactored_code)
            print(f"\n✅ Refactored code saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
    else:
        print("\n🚫 Fixes were not applied. Original code remains unchanged.")

    return feedback