session_memory = {
    "issues": [],
    "feedback": []
}

def remember_issue(issue):
    session_memory["issues"].append(issue)

def remember_feedback(line, description, accepted):
    session_memory["feedback"].append({
        "line": line,
        "description": description,
        "accepted": accepted
    })

def show_session_summary():
    print("\n🧠 Session Summary")
    print("-" * 40)
    print(f"Issues Found: {len(session_memory['issues'])}")
    for i, issue in enumerate(session_memory["issues"], 1):
        print(f"{i}. [Line {issue['line']}] {issue['description']}")

    print(f"\nUser Feedback:")
    for i, fb in enumerate(session_memory["feedback"], 1):
        status = "✅ Accepted" if fb["accepted"] else "❌ Rejected"
        print(f"{i}. Line {fb['line']}: {fb['description']} - {status}")