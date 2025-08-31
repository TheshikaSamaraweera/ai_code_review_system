from langgraph.graph import StateGraph, END
import json
import os

# Define the state (CodeState)
class CodeState:
    def __init__(self):
        self.code = ""
        self.issues = []
        self.feedback = {}
        self.metrics = {}

# Define agent nodes (simplified functions)
def control_agent(state: CodeState) -> CodeState:
    # Coordinates parallel analysis
    state.issues = []
    return state

def quality_agent(state: CodeState) -> CodeState:
    # Detects code quality issues (e.g., poor naming, missing docstrings)
    state.issues.extend([
        {"line": 2, "description": "Poor variable naming", "category": "Quality"},
        {"line": 4, "description": "Missing docstring", "category": "Quality"}
    ])
    return state

def critic_agent(state: CodeState) -> CodeState:
    # Refines issues (e.g., merges duplicates)
    state.issues = [issue for issue in state.issues if "duplicate" not in issue["description"]]
    return state

def refactor_agent(state: CodeState) -> CodeState:
    # Applies fixes based on issues
    state.code = state.code.replace("x =", "user_age =")
    return state

def feedback_loop(state: CodeState) -> CodeState:
    # Checks user feedback or stopping criteria
    state.feedback = {"approved": len(state.issues) < 3}
    return state

def should_continue(state: CodeState) -> str:
    # Conditional edge: continue if issues remain
    return "critic" if not state.feedback.get("approved", False) else END

# Build LangGraph workflow
workflow = StateGraph(CodeState)
workflow.add_node("control", control_agent)
workflow.add_node("quality", quality_agent)
workflow.add_node("critic", critic_agent)
workflow.add_node("refactor", refactor_agent)
workflow.add_node("feedback", feedback_loop)

# Define edges
workflow.set_entry_point("control")
workflow.add_edge("control", "quality")
workflow.add_edge("quality", "critic")
workflow.add_edge("critic", "refactor")
workflow.add_edge("refactor", "feedback")
workflow.add_conditional_edges("feedback", should_continue, {"critic": "critic", END: END})

# Generate Mermaid diagram
def generate_mermaid_diagram(workflow):
    mermaid = ["graph TD"]
    # Add nodes
    for node in workflow.nodes:
        mermaid.append(f"    {node}[{node.capitalize()}<br>{workflow.nodes[node].__ne__}]")
    # Add edges
    for start, ends in workflow.edges.items():
        for end in ends:
            mermaid.append(f"    {start} --> {end}")
    # Add conditional edges
    for start, condition in workflow.conditional_edges.items():
        for condition_value, end in condition[1].items():
            mermaid.append(f"    {start} -->|{condition_value}| {end}")
    return "\n".join(mermaid)

# Save diagram
os.makedirs("architecture_output", exist_ok=True)
with open("architecture_output/architecture.mmd", "w") as f:
    f.write(generate_mermaid_diagram(workflow))
print("Generated Mermaid diagram in 'architecture_output/architecture.mmd'")