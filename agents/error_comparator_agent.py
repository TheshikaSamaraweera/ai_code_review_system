def compare_issues(quality_issues, security_issues, static_issues):
    print("\n🧮 Running Error Comparator Agent...")

    merged = []
    seen = set()

    for issue in quality_issues.get("issues", []):
        key = (issue.get("line"), issue.get("issue").strip().lower())
        seen.add(key)
        merged.append({
            "line": issue["line"],
            "description": issue["issue"],
            "suggestion": issue["suggestion"],
            "source": "AI",
            "severity": issue.get("severity", "medium"),
            "confidence": issue.get("confidence", 0.8)
        })
    
    for issue in security_issues.get("issues", []):
        key = (issue.get("line"), issue.get("issue").strip().lower())
        if key in seen:
            for item in merged:
                if item["line"] == issue["line"] and item["description"].strip().lower() == issue["issue"].strip().lower():
                    item["source"] = "Both"
                    item["severity"] = "high"
                    item["confidence"] = max(item.get("confidence", 0.8), issue.get("confidence", 0.9))
                    break
        else:
            merged.append({
                "line": issue["line"],
                "description": issue["issue"],
                "suggestion": issue["suggestion"],
                "source": "AI",
                "severity": issue.get("severity", "high"),
                "confidence": issue.get("confidence", 0.9)
            })

    for issue in static_issues:
        key = (issue.get("line"), issue.get("issue").strip().lower())
        if key in seen:
            for item in merged:
                if item["line"] == issue["line"] and item["description"].strip().lower() == issue["issue"].strip().lower():
                    item["source"] = "Both"
                    item["severity"] = "high"  # Escalate severity
                    item["confidence"] = max(item.get("confidence", 0.8), issue.get("confidence", 0.8))
                    break
        else:
            merged.append({
                "line": issue["line"],
                "description": issue["issue"],
                "suggestion": issue["suggestion"],
                "source": "Static"
            })

    print(f"\n🧾 Merged Total Issues: {len(merged)}")
    count = {"AI": 0, "Static": 0}
    for m in merged:
        count[m["source"]] += 1
    print(f"   🔍 AI-only: {count['AI']} | 📎 Static-only: {count['Static']} | 🤝 Both: {count['AI'] + count['Static']}")
    return merged
