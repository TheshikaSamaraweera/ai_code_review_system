import os
import tempfile
from utils.file_loader import load_file  # optional if you're using a loader
from agents.quality_agent import run_quality_agent
from agents.static_analysis_agent import run_static_analysis
from agents.error_comparator_agent import compare_issues
from controls.recursive_controller import build_langgraph_loop
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env

def format_initial_analysis_report(quality_results, static_results, merged_issues, code_path):
    """
    Format the initial analysis results in a structured, readable report.
    """
    score = quality_results.get("score", 0)
    ai_issues = quality_results.get("issues", [])
    
    # Calculate statistics
    total_issues = len(merged_issues)
    ai_only_issues = len([i for i in merged_issues if i.get("source") == "AI"])
    static_only_issues = len([i for i in merged_issues if i.get("source") == "Static"])
    both_issues = len([i for i in merged_issues if i.get("source") == "Both"])
    
    # Categorize issues by severity
    high_severity = [i for i in merged_issues if i.get("severity") == "high"]
    medium_severity = [i for i in merged_issues if i.get("severity") == "medium"]
    low_severity = [i for i in merged_issues if i.get("severity") == "low"]
    
    # Generate the report
    report = f"""
{'='*80}
🔍 AI CODE REVIEWER - INITIAL ANALYSIS REPORT
{'='*80}

📁 File Analyzed: {code_path}
📊 Overall Quality Score: {score}/100
🕒 Analysis Timestamp: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*80}
📈 SUMMARY STATISTICS
{'='*80}
• Total Issues Found: {total_issues}
• AI Analysis Issues: {ai_only_issues}
• Static Analysis Issues: {static_only_issues}
• Confirmed Issues (Both): {both_issues}

📊 SEVERITY BREAKDOWN:
• 🔴 High Priority: {len(high_severity)} issues
• 🟡 Medium Priority: {len(medium_severity)} issues
• 🟢 Low Priority: {len(low_severity)} issues

{'='*80}
🔍 DETAILED ISSUE ANALYSIS
{'='*80}
"""
    
    if not merged_issues:
        report += "✅ No issues detected! Your code appears to be clean.\n"
    else:
        # Group issues by source
        sources = {"AI": [], "Static": [], "Both": []}
        for issue in merged_issues:
            source = issue.get("source", "AI")
            sources[source].append(issue)
        
        for source, issues in sources.items():
            if issues:
                source_icon = "🤖" if source == "AI" else "🔧" if source == "Static" else "🤝"
                report += f"\n{source_icon} {source.upper()} ANALYSIS ISSUES ({len(issues)} found):\n"
                report += "-" * 60 + "\n"
                
                for i, issue in enumerate(issues, 1):
                    line_num = issue.get("line", "N/A")
                    description = issue.get("description", "No description")
                    suggestion = issue.get("suggestion", "No suggestion")
                    severity = issue.get("severity", "medium")
                    confidence = issue.get("confidence", 0.8)
                    
                    # Severity icons
                    severity_icon = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                    
                    report += f"{i:2d}. Line {line_num:3d} | {severity_icon} {severity.upper()}\n"
                    report += f"    📝 Issue: {description}\n"
                    report += f"    💡 Suggestion: {suggestion}\n"
                    report += f"    🎯 Confidence: {confidence:.1%}\n"
                    report += "\n"
    
    # Quality score interpretation
    report += f"{'='*80}\n"
    report += "📊 QUALITY SCORE INTERPRETATION\n"
    report += "="*80 + "\n"
    
    if score >= 90:
        report += "🏆 EXCELLENT (90-100): Code follows best practices excellently!\n"
    elif score >= 80:
        report += "✅ GOOD (80-89): Code is well-structured with minor improvements possible.\n"
    elif score >= 70:
        report += "⚠️  FAIR (70-79): Code needs some improvements but is generally acceptable.\n"
    elif score >= 60:
        report += "🔧 NEEDS WORK (60-69): Several issues need to be addressed.\n"
    else:
        report += "🚨 POOR (0-59): Significant refactoring required.\n"
    
    report += f"\n🎯 RECOMMENDATIONS:\n"
    if total_issues == 0:
        report += "• Your code is in excellent condition!\n"
        report += "• Consider running optimization for performance improvements.\n"
    elif len(high_severity) > 0:
        report += f"• 🔴 Address {len(high_severity)} high-priority issues first.\n"
    if len(medium_severity) > 0:
        report += f"• 🟡 Review {len(medium_severity)} medium-priority issues.\n"
    if score < 80:
        report += "• Consider running iterative optimization to improve code quality.\n"
    
    report += f"\n{'='*80}\n"
    return report


def format_iteration_summary(final):
    """
    Format the final iteration summary in a structured report.
    """
    best_code = final.get("best_code", "[No final code]")
    history = final.get("history", [])
    
    report = f"""
{'='*80}
🎯 ITERATIVE OPTIMIZATION COMPLETE
{'='*80}

📊 FINAL RESULTS:
• Total Iterations: {len(history)}
• Best Quality Score: {final.get('best_score', 'N/A')}
• Final Code Length: {len(best_code)} characters

{'='*80}
📚 ITERATION HISTORY
{'='*80}
"""
    
    for i, step in enumerate(history, 1):
        iteration = step.get('iteration', f'{i}.0')
        score = step.get('score', 'N/A')
        issues_count = len(step.get('refined_issues', []))
        optimization_applied = step.get('optimization_applied', False)
        optimization_suggestions = step.get('optimization_suggestions', [])
        
        report += f"\n🧾 Iteration {iteration}:\n"
        report += f"   📊 Quality Score: {score}\n"
        report += f"   🔍 Issues Addressed: {issues_count}\n"
        
        if optimization_applied:
            report += f"   🚀 Optimization Applied: Yes ({len(optimization_suggestions)} suggestions)\n"
        else:
            report += f"   🚀 Optimization Applied: No\n"
        
        # Show code preview
        refactored_code = step.get('refactored_code', '')
        if refactored_code:
            preview = refactored_code[:150] + "..." if len(refactored_code) > 150 else refactored_code
            report += f"   📝 Code Preview: {preview}\n"
        
        report += "-" * 40 + "\n"
    
    report += f"\n{'='*80}\n"
    report += "✅ FINAL REFACTORED CODE\n"
    report += "="*80 + "\n"
    report += best_code
    report += f"\n{'='*80}\n"
    
    return report


def main():
    # Load API key
    api_key = load_dotenv()
    # Load code file
    code_path = input("📄 Enter the path to your Python code (e.g., sample_code.py): ").strip()
    if not os.path.exists(code_path):
        print("❌ File not found.")
        return

    with open(code_path, "r") as f:
        code = f.read()

    print("\n🔍 Phase 1: Running Initial Analysis...")

    # Run Quality Agent
    quality_results = run_quality_agent(code, api_key)
    score = quality_results.get("score", 0)

    # Run Static Analysis
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as temp_file:
        temp_file.write(code)
        temp_path = temp_file.name
    static_results = run_static_analysis(temp_path)
    os.remove(temp_path)

    # Merge AI and static tool issues
    merged_issues = compare_issues(quality_results, static_results)

    # Display formatted report
    report = format_initial_analysis_report(quality_results, static_results, merged_issues, code_path)
    print(report)

    # Ask if user wants to apply fixes and enter iterative optimization
    answer = input("\n🤖 Apply fixes and optimize code iteratively? (y/N): ").strip().lower()
    if answer != "y":
        print("\n🚫 Exiting after initial review. No changes applied.")
        return

    print("\n♻️ Entering Iterative Optimization Mode...\n")

    # Initialize LangGraph loop state
    state = {
        "api_key": api_key,
        "code": code,
        "iteration": 0,
        "continue_": True,
        "auto_refine": True,
        "max_outer_iterations": 4,
        "min_score_threshold": 90.0,
        "max_high_severity_issues": 0,
        "history": [],
        "best_code": code,
        "best_score": score,
        "score": score,
        "no_improvement_count": 0,
        "best_refined_issues": []
    }

    graph = build_langgraph_loop()
    final = graph.invoke(state)

    # Display formatted final summary
    final_report = format_iteration_summary(final)
    print(final_report)

if __name__ == "__main__":
    main()
