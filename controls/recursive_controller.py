import tempfile
import os
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


def build_langgraph_loop():
    def refinement_step(state: CodeState) -> CodeState:
        code = state["code"]
        api_key = state["api_key"]
        iteration = state.get("iteration", 0)
        history = state.get("history", [])

        print(f"\n🔁 Refinement Iteration {iteration}")

        quality_results = run_quality_agent(code, api_key)

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name

        static_results = run_static_analysis(temp_path)
        os.remove(temp_path)

        merged_issues = compare_issues(quality_results, static_results)
        refined_issues = run_critic_agent(code, merged_issues, api_key)
        refactored_code = run_refactor_agent(code, refined_issues, api_key)

        history.append({
            "iteration": iteration,
            "original_code": code,
            "refined_issues": refined_issues,
            "refactored_code": refactored_code
        })

        print(f"\n🌀 Iteration {iteration} complete.")
        response = input("🔁 Run another refinement loop? (y/N): ").strip().lower()
        continue_loop = response == "y"

        return {
            "code": refactored_code or code,
            "api_key": api_key,
            "iteration": iteration + 1,
            "history": history,
            "continue_": continue_loop,
            "refactored_code": refactored_code or code,
        }

    def should_continue(state: CodeState) -> Literal["refine", "end"]:
        return "refine" if state.get("continue_", False) else "end"

    # No longer use define_schema(CodeState)
    define_schema()  # Just needed to activate schema checking

    graph = StateGraph(CodeState)  # Pass schema here instead
    graph.add_node("refine", refinement_step)
    graph.set_entry_point("refine")
    graph.add_conditional_edges("refine", should_continue, {
        "refine": "refine",
        "end": "__end__"
    })

    return graph.compile()
