import difflib

def show_code_diff(original, modified):
    original_lines = original.strip().splitlines()
    modified_lines = modified.strip().splitlines()

    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile='original.py',
        tofile='refactored.py',
        lineterm=''
    )

    print("\n🆚 Code Diff (Before vs After):\n")
    for line in diff:
        if line.startswith('+'):
            print(f"\033[92m{line}\033[0m")  # Green for additions
        elif line.startswith('-'):
            print(f"\033[91m{line}\033[0m")  # Red for deletions
        else:
            print(line)
