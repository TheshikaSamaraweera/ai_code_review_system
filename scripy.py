import csv

# manually define issue annotations (line_number: issue_type)
ISSUES = {
    3: "Unused Imports",
    5: "Naming Style",
    6: "Formatting / Style",
    7: "Inconsistent Naming",
    9: "Poor Variable Naming",
    10: "Hardcoded Password",
    11: "Hardcoded Secret",
    14: "Naming Style",
    16: "Unused Variables",
    19: "Redundant Operation",
    22: "Division by Zero Risk",
    25: "Inefficient Loop",
    27: "Dead Code",
    30: "Unbounded Recursion",
    33: "Security - eval",
    36: "Security - exec",
    39: "None Comparison",
    44: "File Handling (no context manager)",
    49: "Shadowing Builtins",
    52: "Long Method",
    54: "Runtime Bug",
    55: "Bare Except",
    57: "Performance (Memory)",
    62: "Duplicate Code",
    66: "Unused Method",
    72: "Inefficient String Concatenation",
    77: "SQL Injection",
    81: "Magic Number",
    85: "Mutable Default Arg",
    89: "Pointless Condition",
    93: "Deep Nesting"
}

def build_csv(input_file="bad_class.py", output_file="dataset.csv"):
    with open(input_file, "r") as f:
        lines = f.readlines()

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["line", "code", "has_issue", "issue_type"])

        for idx, line in enumerate(lines, start=1):
            issue_type = ISSUES.get(idx, "")
            has_issue = "True" if issue_type else "False"
            writer.writerow([idx, line.strip(), has_issue, issue_type])

    print(f"✅ Dataset saved as {output_file}")

if __name__ == "__main__":
    build_csv()
