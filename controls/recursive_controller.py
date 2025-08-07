import tempfile
import os
import json
from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph
from agents.quality_agent import run_quality_agent
from agents.static_analysis_agent import run_static_analysis
from agents.error_comparator_agent import compare_issues
from agents.critic_agent import run_critic_agent
from agents.refactor_agent import run_refactor_agent
from agents.optimization_agent import run_optimization_agent
from memory.session_memory import remember_issue

class CodeState(TypedDict):
    code: str
    api_key: str
    iteration: int
    history: List[dict]
    continue_: bool
    best_code: str
    best_score: float
    best_issues: List[dict]
    issue_count: int
    issues_fixed: int
    feedback: List[dict]
    min_score_threshold: float
    max_high_severity_issues: int
    max_iterations: int
    context: dict
    optimization_applied: bool


def prioritize_issues(issues: List[dict], feedback: List[dict]) -> List[dict]:
    """Prioritize issues based on user feedback (e.g., deprioritize rejected suggestions)."""
    prioritized = []
    rejected_issues = {fb["line"]: fb["description"] for fb in feedback if not fb["accepted"]}

    for issue in issues:
        key = (issue["line"], issue["description"].strip().lower())
        if key not in [(fb["line"], fb["description"].strip().lower()) for fb in rejected_issues.values()]:
            # Boost priority for high-severity issues or those not rejected
            issue["priority"] = 1.0 if issue.get("severity") == "high" else 0.8
            prioritized.append(issue)
        else:
            # Deprioritize rejected issues
            issue["priority"] = 0.5
            prioritized.append(issue)

    return sorted(prioritized, key=lambda x: x["priority"], reverse=True)


def build_langgraph_loop():
    def refinement_step(state: CodeState) -> CodeState:
        code = state["code"]
        api_key = state["api_key"]
        iteration = state.get("iteration", 0)
        history = state.get("history", [])
        feedback = state.get("feedback", [])
        min_score_threshold = state.get("min_score_threshold", 95.0)
        max_high_severity_issues = state.get("max_high_severity_issues", 0)
        max_iterations = state.get("max_iterations", 5)
        context = state.get("context", {})
        optimization_applied = state.get("optimization_applied", False)

        print(f"\n🔁 Iteration {iteration}\n")

        # Step 1: Analyze code
        quality_results = run_quality_agent(code, api_key, context)

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name
        static_results = run_static_analysis(temp_path)
        os.remove(temp_path)
        
        # Merge and refine issues
        merged_issues = compare_issues(quality_results, static_results)
        refined_issues = run_critic_agent(code, merged_issues, api_key)

        # Prioritize issues based on feedback
        refined_issues = prioritize_issues(refined_issues, feedback)

        print(f"\n📌 Refined Issues ({len(refined_issues)}):")
        print(json.dumps(refined_issues, indent=2))

        # Step 2: Apply suggestions
        refactored_code = run_refactor_agent(code, refined_issues, api_key)
        if not refactored_code:
            print("⚠️ Refactor Agent failed to produce valid code. Stopping.")
            return {**state, "continue_": False}

        # Validate fixes by re-analyzing
        new_quality_results = run_quality_agent(refactored_code, api_key, context)
        new_score = new_quality_results.get("score", 0)
        new_issues = new_quality_results.get("issues", [])
        high_severity_count = len([i for i in new_issues if i.get("severity") == "high"])

        # Step 3: Optimization (if no high-severity issues and significant progress)
        final_code = refactored_code
        optimization_suggestions = []
        if not optimization_applied and high_severity_count == 0 and len(new_issues) < len(refined_issues) // 2:
            print("\n🚀 Running Optimization Agent...")
            optimization_suggestions = run_optimization_agent(refactored_code, api_key)
            if optimization_suggestions:
                optimization_issues = [
                    {
                        "line": s.get("line", 0),
                        "description": s.get("description", ""),
                        "suggestion": s.get("suggestion", ""),
                        "source": "Optimization",
                        "severity": "medium",
                        "confidence": 0.8
                    } for s in optimization_suggestions
                ]
                final_code = run_refactor_agent(refactored_code, optimization_issues, api_key)
                optimization_applied = True
                print("✅ Optimization applied.")

        # Step 4: Update state
        issues_fixed = len(refined_issues) - len(new_issues)
        best_code = state.get("best_code", code)
        best_score = state.get("best_score", -1)
        best_issues = state.get("best_issues", refined_issues)

        if new_score > best_score or len(new_issues) < len(best_issues):
            best_code = final_code
            best_score = new_score
            best_issues = new_issues

        history.append({
            "iteration": iteration,
            "score": new_score,
            "issue_count": len(new_issues),
            "issues_fixed": issues_fixed,
            "high_severity_count": high_severity_count,
            "refactored_code": final_code[:200] + "..." if len(final_code) > 200 else final_code,
            "optimization_applied": optimization_applied,
            "optimization_suggestions": optimization_suggestions
        })

        # Step 5: Stopping criteria
        continue_loop = (
                len(new_issues) > 0 and
                issues_fixed > 0 and
                new_score < min_score_threshold and
               # high_severity_count <= max_high_severity_issues and
                iteration + 1 < max_iterations
        )

        return {
            "code": final_code,
            "api_key": api_key,
            "iteration": iteration + 1,
            "history": history,
            "continue_": continue_loop,
            "best_code": best_code,
            "best_score": best_score,
            "best_issues": best_issues,
            "issue_count": len(new_issues),
            "issues_fixed": issues_fixed,
            "feedback": feedback,
            "min_score_threshold": min_score_threshold,
            "max_high_severity_issues": max_high_severity_issues,
            "max_iterations": max_iterations,
            "context": context,
            "optimization_applied": optimization_applied
        }

    def should_continue(state: CodeState) -> Literal["refine", "end"]:
        return "refine" if state.get("continue_", False) else "end"

    graph = StateGraph(CodeState)
    graph.add_node("refine", refinement_step)
    graph.set_entry_point("refine")
    graph.add_conditional_edges("refine", should_continue, {
        "refine": "refine",
        "end": "__end__"
    })

    return graph.compile()