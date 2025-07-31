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
    auto_refine: bool  # <--- add this line
    max_outer_iterations:int


def build_langgraph_loop():
    def refinement_step(state: CodeState) -> CodeState:
        code = state["code"]
        api_key = state["api_key"]
        outer_iteration = state.get("iteration", 0)
        history = state.get("history", [])
        auto_refine = state.get("auto_refine", True)
        max_outer_iterations = 4

        best_code = state.get("best_code", code)
        best_score = state.get("best_score", -1)
        best_refined_issues = state.get("best_refined_issues", [])

        print(f"\n🔁 Outer Iteration {outer_iteration} (User approved)")

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

        # Step 3: Compare
        merged_issues = compare_issues(quality_results, static_results)

        # Step 4: Critic
        refined_issues = run_critic_agent(code, merged_issues, api_key)

        # Print formatted refined issues
        print(f"\n📌 Refined Issues:")
        print(json.dumps(refined_issues, indent=2))

        # Step 5: Refactor
        refactored_code = run_refactor_agent(code, refined_issues, api_key)

        # Track best by score
        if score > best_score:
            best_code = refactored_code
            best_score = score
            best_refined_issues = refined_issues

        # Save this step
        history.append({
            "iteration": f"{outer_iteration}.0",
            "score": score,
            "refined_issues": refined_issues,
            "refactored_code": refactored_code
        })

        # Loop control
        continue_loop = outer_iteration + 1 < max_outer_iterations

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
    def refine_once(code: str, api_key: str, iteration: int):
        quality_results = run_quality_agent(code, api_key)
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name

        static_results = run_static_analysis(temp_path)
        os.remove(temp_path)

        merged_issues = compare_issues(quality_results, static_results)
        refined_issues = run_critic_agent(code, merged_issues, api_key)
        refactored_code = run_refactor_agent(code, refined_issues, api_key)

        return refactored_code, refined_issues

    return graph.compile()
