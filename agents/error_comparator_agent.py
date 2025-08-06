def compare_issues(ai_issues, static_issues):
    print("🧮 Running Error Comparator...")

    merged = []
    seen = set()

    for issue in ai_issues.get("issues", []):
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

    # Calculate statistics
    count = {"AI": 0, "Static": 0, "Both": 0}
    for m in merged:
        count[m["source"]] += 1
    
    print(f"✅ Error Comparator completed - Merged {len(merged)} issues (AI: {count['AI']}, Static: {count['Static']}, Both: {count['Both']})")
    return merged
