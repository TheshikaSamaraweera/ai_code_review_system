# /media/theshika/F4AA5B09AA5AC7AE/ai_code_review_system/generate_synthetic_data.py
import os
import random


def generate_synthetic_code(num_samples=10, output_dir='test_data/synthetic'):
    os.makedirs(output_dir, exist_ok=True)
    issue_types = ['long_method', 'magic_number', 'high_complexity', 'duplicate_code', 'hardcoded_secret']

    for i in range(num_samples):
        code = """
def normal_function(x):
    return x + 1

"""
        num_issues = random.randint(1, 3)
        for _ in range(num_issues):
            issue = random.choice(issue_types)
            if issue == 'long_method':
                code += "def long_method():\n" + "    pass\n" * 60
            elif issue == 'magic_number':
                code += "def func():\n    return 42 + 1337  # Magic numbers\n"
            elif issue == 'high_complexity':
                code += "def complex_func(x):\n" + "    if x > 0:\n" * 15 + "        pass\n"
            elif issue == 'duplicate_code':
                dup_block = "    print('dup')\n" * 5
                code += f"def func1():\n{dup_block}def func2():\n{dup_block}"
            elif issue == 'hardcoded_secret':
                code += "API_KEY = 'sk-1234567890'  # Hardcoded secret\n"

        file_path = os.path.join(output_dir, f'sample_{i}.py')
        with open(file_path, 'w') as f:
            f.write(code)

    print(f"Generated {num_samples} synthetic samples in {output_dir}")


if __name__ == "__main__":
    generate_synthetic_code()