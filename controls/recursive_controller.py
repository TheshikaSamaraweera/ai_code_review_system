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


class CodeState(TypedDict):
    code: str
    api_key: str
    iteration: int
    history: List[dict]
    continue_: bool
    refactored_code: str
    auto_refine: bool
    max_outer_iterations: int
    best_code: str
    best_score: float
    score: float
    no_improvement_count: int
    best_refined_issues: List[dict]


def build_langgraph_loop():
    def refinement_step(state: CodeState) -> CodeState:
        code = state["code"]
        api_key = state["api_key"]
        outer_iteration = state.get("iteration", 0)
        history = state.get("history", [])
        auto_refine = state.get("auto_refine", True)
        max_outer_iterations = state.get("max_outer_iterations", 4)

        print(f"\n🔁 Outer Iteration {outer_iteration} (User approved)\n")

        # Step 1: Quality Agent
        quality_results = run_quality_agent(code, api_key)
        score = quality_results.get("score", 0)
        ai_issues = quality_results.get("issues", [])

        # Step 2: Static Analysis
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name
        static_results = run_static_analysis(temp_path)
        os.remove(temp_path)

        # Step 3: Merge issues
        merged_issues = compare_issues(quality_results, static_results)

        # Step 4: Refine issues
        refined_issues = run_critic_agent(code, merged_issues, api_key)

        print(f"\n📌 Refined Issues:")
        print(json.dumps(refined_issues, indent=2))

        # Step 5: Refactor
        refactored_code = run_refactor_agent(code, refined_issues, api_key)

        # Load previous bests
        best_code = state.get("best_code", code)
        best_score = state.get("best_score", -1)
        best_refined_issues = state.get("best_refined_issues", [])
        prev_score = state.get("score", 0)
        no_improvement_count = state.get("no_improvement_count", 0)

        # Check for improvement
        if score > best_score:
            best_code = refactored_code
            best_score = score
            best_refined_issues = refined_issues
            no_improvement_count = 0
        elif score <= prev_score:
            no_improvement_count += 1

        # Save history
        history.append({
            "iteration": f"{outer_iteration}.0",
            "score": score,
            "refined_issues": refined_issues,
            "refactored_code": refactored_code
        })

        # Control loop continuation
        continue_loop = (outer_iteration + 1 < max_outer_iterations) and (no_improvement_count < 2)

        return {
            "code": refactored_code,
            "api_key": api_key,
            "iteration": outer_iteration + 1,
            "history": history,
            "continue_": continue_loop,
            "refactored_code": refactored_code,
            "auto_refine": True,
            "best_code": best_code,
            "best_score": best_score,
            "score": score,
            "no_improvement_count": no_improvement_count,
            "max_outer_iterations": max_outer_iterations,
            "best_refined_issues": best_refined_issues
        }

    def should_continue(state: CodeState) -> Literal["refine", "end"]:
        return "refine" if state.get("continue_", False) else "end"

    define_schema()

    graph = StateGraph(CodeState)
    graph.add_node("refine", refinement_step)
    graph.set_entry_point("refine")
    graph.add_conditional_edges("refine", should_continue, {
        "refine": "refine",
        "end": "__end__"
    })

    return graph.compile()
