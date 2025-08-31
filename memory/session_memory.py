session_memory = {
    "issues": [],
    "feedback": []
}

def remember_issue(issue):
    required_keys = ['line', 'description', 'suggestion', 'severity', 'confidence']
    normalized_issue = {key: issue.get(key, 'Unknown ' + key) for key in required_keys}
    session_memory["issues"].append(normalized_issue)

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
        line = issue.get('line', 'Unknown line')
        description = issue.get('description', 'No description provided')
        print(f"{i}. [Line {line}] {description}")
    print(f"\nUser Feedback:")
    for i, fb in enumerate(session_memory["feedback"], 1):
        status = "✅ Accepted" if fb['accepted'] else "❌ Rejected"
        print(f"{i}. Line {fb['line']}: {fb['description']} - {status}")