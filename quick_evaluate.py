# /media/theshika/F4AA5B09AA5AC7AE/ai_code_review_system/quick_evaluate.py
import argparse
import os
import json
from dotenv import load_dotenv
from evaluation.metrics_calculator import CodeAnalysisEvaluator
from agents.quality_agent import run_quality_agent
from agents.security_agent import run_security_agent
from agents.code_smell_agent import run_code_smell_agent

load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')


def quick_evaluate_file(file_path):
    evaluator = CodeAnalysisEvaluator([
        run_quality_agent,
        run_security_agent,
        run_code_smell_agent
    ])
    result = evaluator.evaluate_file(file_path, API_KEY)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Path to file or --sample for test')
    args = parser.parse_args()

    if args.file == '--sample':
        with open('temp_sample.py', 'w') as f:
            f.write("def long_func():\n" + "    pass\n" * 60 + "\nreturn 42")
        quick_evaluate_file('temp_sample.py')
        os.remove('temp_sample.py')
    else:
        quick_evaluate_file(args.file)