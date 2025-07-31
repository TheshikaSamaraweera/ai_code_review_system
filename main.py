import argparse
import json

from utils.file_loader import load_file
from controls.recursive_controller import build_langgraph_loop

def main():
    parser = argparse.ArgumentParser(description="AI Code Review CLI with Recursive LangGraph")
    parser.add_argument('--file', type=str, required=True, help='Path to the source code file')
    args = parser.parse_args()

    # Load source code
    initial_code = load_file(args.file)

    # Build LangGraph loop
    graph = build_langgraph_loop()

    # Initial state
    state = {
        "code": initial_code,
        "api_key": "AIzaSyDaW3FIrAlu3Kf_iLIDt8j5wlOw3lXTDiY",  # 🔐 Replace with environment variable for production
        "iteration": 0,
        "history": [],
        "continue_": True,
        "refactored_code": initial_code,
        "auto_refine": None,
        "max_outer_iterations": 5
    }

    final = graph.invoke(state)

    # Show best refined issues
    print("\n📌 Final Refined Issues:")
    print(json.dumps(final.get("best_refined_issues", []), indent=2))

    # Final result
    print("\n✅ Final Refactored Code:\n")
    print(final.get("best_code", "[No code returned]"))

    # Iteration summary
    print("\n📚 Iteration Summary:")
    for step in final["history"]:
        print(f"\n🧾 Iteration {step['iteration']}:")
        print(f"   Quality Score: {step.get('score', '?')}")
        print("   Code Preview:")
        print(step["refactored_code"][:200])


if __name__ == "__main__":
    main()
