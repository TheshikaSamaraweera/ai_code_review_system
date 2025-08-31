# /media/theshika/F4AA5B09AA5AC7AE/ai_code_review_system/evaluation/run_evaluation.py
import os
import json
import statistics
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from .metrics_calculator import CodeAnalysisEvaluator
from agents.quality_agent import run_quality_agent
from agents.security_agent import run_security_agent
from agents.code_smell_agent import run_code_smell_agent

load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')


class EvaluationRunner:
    def __init__(self, test_dir='test_data/synthetic'):
        self.evaluator = CodeAnalysisEvaluator([
            run_quality_agent,
            run_security_agent,
            run_code_smell_agent
        ])
        self.test_dir = test_dir
        self.results_dir = 'evaluation/results'
        os.makedirs(self.results_dir, exist_ok=True)

    def run(self):
        # If test_dir doesn't exist, create a single sample file
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir, exist_ok=True)
            with open(os.path.join(self.test_dir, 'sample_0.py'), 'w') as f:
                f.write("def long_func():\n" + "    pass\n" * 60 + "\nAPI_KEY = 'sk-1234567890'")

        files = [os.path.join(self.test_dir, f) for f in os.listdir(self.test_dir) if f.endswith('.py')]
        if not files:
            print("No test files found. Please generate test data.")
            return

        results = []
        for file in files:
            result = self.evaluator.evaluate_file(file, API_KEY)
            results.append(result)

        agg = {
            'avg_precision': statistics.mean(r['precision'] for r in results),
            'avg_recall': statistics.mean(r['recall'] for r in results),
            'avg_f1': statistics.mean(r['f1'] for r in results),
            'total_tp': sum(r['tp'] for r in results),
            'total_fp': sum(r['fp'] for r in results),
            'total_fn': sum(r['fn'] for r in results)
        }

        with open(os.path.join(self.results_dir, 'detailed_results.json'), 'w') as f:
            json.dump(results, f, indent=2)
        with open(os.path.join(self.results_dir, 'summary.json'), 'w') as f:
            json.dump(agg, f, indent=2)

        print("Aggregate Metrics:")
        print(json.dumps(agg, indent=2))

        self._visualize_results(results)

    def _visualize_results(self, results):
        df = pd.DataFrame([{
            'file': r['file'],
            'precision': r['precision'],
            'recall': r['recall'],
            'f1': r['f1']
        } for r in results])

        sns.barplot(data=df.melt(id_vars='file'), x='file', y='value', hue='variable')
        plt.title('Performance per File')
        plt.xticks(rotation=45)
        plt.savefig(os.path.join(self.results_dir, 'performance.png'))
        plt.close()


if __name__ == "__main__":
    runner = EvaluationRunner()
    runner.run()