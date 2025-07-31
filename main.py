import argparse
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
    }

    # Run the graph
    final = graph.invoke(state)

    # Display final code
    print("\n✅ Final Refactored Code:\n")
    print(final.get("refactored_code", "[No code returned]"))

    # Show summary of iterations
    print("\n📚 Iteration Summary:")
    for step in final["history"]:
        print(f"\n🧾 Iteration {step['iteration']}:")
        print("Refined Issues:", len(step["refined_issues"]))
        print("Code Preview:\n", step["refactored_code"][:200])

if __name__ == "__main__":
    main()
