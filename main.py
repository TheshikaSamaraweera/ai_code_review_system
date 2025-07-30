import argparse
from utils.file_loader import load_file
from utils.language_detector import detect_language
from agents.control_agent import run_control_agent  # ⬅️ Import added

def main():
    parser = argparse.ArgumentParser(description="AI Code Review CLI")
    parser.add_argument('--file', type=str, required=True, help='Path to the source code file')
    args = parser.parse_args()

    try:
        code = load_file(args.file)
        language = detect_language(args.file)

        print("\n✅ File Loaded Successfully")
        print(f"📄 File: {args.file}")
        print(f"🧠 Detected Language: {language}")
        print(f"🔢 Number of lines: {len(code.splitlines())}")

        # Run Control Agent
        run_control_agent(code, language)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
