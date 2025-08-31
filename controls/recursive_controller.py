import tempfile
import os
import json
from typing import TypedDict, List, Literal

from langgraph.graph import StateGraph, define_schema

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
    previous_scores: List[float]  # Track score history for convergence
    stagnation_count: int  # Track consecutive iterations without improvement


def prioritize_issues(issues: List[dict], feedback: List[dict]) -> List[dict]:
    """Prioritize issues based on user feedback and severity."""
    prioritized = []
    rejected_descriptions = {fb["description"].strip().lower() for fb in feedback if not fb["accepted"]}

    for issue in issues:
        issue_desc = issue.get("description", "").strip().lower()

        # Skip issues that were explicitly rejected by user
        if issue_desc in rejected_descriptions:
            continue

        # Set priority based on severity and user feedback
        severity = issue.get("severity", "medium")
        if severity == "high":
            issue["priority"] = 1.0
        elif severity == "medium":
            issue["priority"] = 0.7
        else:
            issue["priority"] = 0.4

        prioritized.append(issue)

    return sorted(prioritized, key=lambda x: x.get("priority", 0.5), reverse=True)


def has_converged(scores: List[float], threshold: float = 2.0) -> bool:
    """Check if quality scores have converged (stopped improving significantly)."""
    if len(scores) < 3:
        return False

    # Check if last 3 scores are within threshold of each other
    recent_scores = scores[-3:]
    max_diff = max(recent_scores) - min(recent_scores)
    return max_diff < threshold


def build_langgraph_loop():
    def refinement_step(state: CodeState) -> CodeState:
        code = state["code"]
        api_key = state["api_key"]
        iteration = state.get("iteration", 0)
        history = state.get("history", [])
        feedback = state.get("feedback", [])
        min_score_threshold = state.get("min_score_threshold", 85.0)  # More realistic threshold
        max_high_severity_issues = state.get("max_high_severity_issues", 0)
        max_iterations = state.get("max_iterations", 5)
        context = state.get("context", {})
        optimization_applied = state.get("optimization_applied", False)
        previous_scores = state.get("previous_scores", [])
        stagnation_count = state.get("stagnation_count", 0)

        print(f"\n🔁 Iteration {iteration + 1}/{max_iterations}")
        print("-" * 50)

        # Step 1: Analyze current code
        print("📊 Analyzing code quality...")
        quality_results = run_quality_agent(code, api_key, context)
        current_score = quality_results.get("score", 0)

        # Create temporary file for static analysis
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name

        try:
            static_results = run_static_analysis(temp_path)
        finally:
            os.remove(temp_path)

        # Merge and refine issues
        print("🔍 Identifying and refining issues...")
        merged_issues = compare_issues(quality_results, static_results)
        refined_issues = run_critic_agent(code, merged_issues, api_key)

        # Prioritize issues based on feedback
        refined_issues = prioritize_issues(refined_issues, feedback)

        print(f"📋 Found {len(refined_issues)} issues to address")

        # Track scores for convergence detection
        previous_scores.append(current_score)

        # Check for improvement
        improved = False
        if len(previous_scores) > 1:
            if current_score > previous_scores[-2]:
                improved = True
                stagnation_count = 0
            else:
                stagnation_count += 1

        # Step 2: Apply fixes if there are actionable issues
        refactored_code = code
        if refined_issues:
            print("🔧 Applying fixes...")
            refactored_code = run_refactor_agent(code, refined_issues, api_key)

            if not refactored_code or refactored_code.strip() == "":
                print("⚠️ Refactor Agent failed to produce valid code. Using original code.")
                refactored_code = code
        else:
            print("✅ No issues found to fix!")

        # Step 3: Re-evaluate refactored code
        print("📊 Re-evaluating refactored code...")
        new_quality_results = run_quality_agent(refactored_code, api_key, context)
        new_score = new_quality_results.get("score", current_score)
        new_issues = new_quality_results.get("issues", [])
        high_severity_count = len([i for i in new_issues if i.get("severity") == "high"])

        # Step 4: Apply optimization if conditions are met
        final_code = refactored_code
        optimization_suggestions = []

        if (not optimization_applied and
                high_severity_count <= max_high_severity_issues and
                len(new_issues) <= len(refined_issues) // 2 and
                new_score >= 75):  # Only optimize reasonably good code

            print("🚀 Applying optimizations...")
            optimization_suggestions = run_optimization_agent(refactored_code, api_key)

            if optimization_suggestions:
                optimization_issues = [
                    {
                        "line": s.get("line", 0),
                        "description": s.get("description", ""),
                        "suggestion": s.get("suggestion", ""),
                        "source": "Optimization",
                        "severity": "low",  # Optimizations are usually low priority
                        "confidence": 0.8
                    } for s in optimization_suggestions
                ]

                optimized_code = run_refactor_agent(refactored_code, optimization_issues, api_key)
                if optimized_code and optimized_code.strip():
                    final_code = optimized_code
                    optimization_applied = True
                    print("✅ Optimization applied successfully.")

        # Step 5: Update best code if this iteration improved things
        best_code = state.get("best_code", code)
        best_score = state.get("best_score", 0)
        best_issues = state.get("best_issues", refined_issues)

        # Update best results if we improved
        if new_score > best_score or (new_score == best_score and len(new_issues) < len(best_issues)):
            best_code = final_code
            best_score = new_score
            best_issues = new_issues
            print(f"🎯 New best score: {best_score:.1f} (improvement: +{best_score - state.get('best_score', 0):.1f})")

        # Calculate issues fixed this iteration
        issues_fixed = max(0, len(refined_issues) - len(new_issues))

        # Record iteration history
        iteration_record = {
            "iteration": iteration + 1,
            "score": new_score,
            "issue_count": len(new_issues),
            "issues_fixed": issues_fixed,
            "high_severity_count": high_severity_count,
            "improved": improved,
            "optimization_applied": optimization_applied,
            "optimization_suggestions_count": len(optimization_suggestions)
        }
        history.append(iteration_record)

        # Step 6: Determine if we should continue
        should_continue = True
        stop_reason = None

        # Check various stopping criteria
        if iteration + 1 >= max_iterations:
            should_continue = False
            stop_reason = f"Reached maximum iterations ({max_iterations})"

        elif len(new_issues) == 0:
            should_continue = False
            stop_reason = "No issues remaining"

        elif new_score >= min_score_threshold and high_severity_count <= max_high_severity_issues:
            should_continue = False
            stop_reason = f"Quality threshold reached (score: {new_score:.1f} >= {min_score_threshold})"

        elif stagnation_count >= 2:
            should_continue = False
            stop_reason = "No improvement for 2 consecutive iterations"

        elif has_converged(previous_scores):
            should_continue = False
            stop_reason = "Quality scores have converged"

        elif issues_fixed == 0 and len(refined_issues) > 0:
            should_continue = False
            stop_reason = "No issues were fixed this iteration"

        if stop_reason:
            print(f"🛑 Stopping: {stop_reason}")
        else:
            print(f"🔄 Continuing to next iteration...")

        return {
            "code": final_code,
            "api_key": api_key,
            "iteration": iteration + 1,
            "history": history,
            "continue_": should_continue,
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
            "optimization_applied": optimization_applied,
            "previous_scores": previous_scores,
            "stagnation_count": stagnation_count
        }

    def should_continue(state: CodeState) -> Literal["refine", "end"]:
        """Decide whether to continue refining or end the process."""
        return "refine" if state.get("continue_", False) else "end"

    # Build the graph
    define_schema()
    graph = StateGraph(CodeState)
    graph.add_node("refine", refinement_step)
    graph.set_entry_point("refine")
    graph.add_conditional_edges("refine", should_continue, {
        "refine": "refine",
        "end": "__end__"
    })

    return graph.compile()