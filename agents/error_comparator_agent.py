def compare_issues(ai_issues, static_issues):
    print("\n🧮 Running Error Comparator Agent...")

    merged = []
    seen = set()

    # Normalize AI issues
    for issue in ai_issues.get("issues", []):
        key = (issue.get("line"), issue.get("issue").strip().lower())
        seen.add(key)
        merged.append({
            "line": issue["line"],
            "description": issue["issue"],
            "suggestion": issue["suggestion"],
            "source": "AI"
        })

    # Normalize Static issues and merge
    for issue in static_issues:
        key = (issue.get("line"), issue.get("issue").strip().lower())
        if key in seen:
            for item in merged:
                if item["line"] == issue["line"] and item["description"].strip().lower() == issue["issue"].strip().lower():
                    item["source"] = "Both"
                    break
        else:
            merged.append({
                "line": issue["line"],
                "description": issue["issue"],
                "suggestion": issue["suggestion"],
                "source": "Static"
            })

    print(f"🧾 Merged Total Issues: {len(merged)}")
    count = {"AI": 0, "Static": 0, "Both": 0}
    for m in merged:
        count[m["source"]] += 1

    print(f"   🔍 AI-only: {count['AI']} | 📎 Static-only: {count['Static']} | 🤝 Both: {count['Both']}")
    return merged
