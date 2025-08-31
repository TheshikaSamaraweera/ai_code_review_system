import ast
import re
import os
import json
import statistics
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from typing import List, Dict, Any


class SyntacticGroundTruthGenerator:
    """Generates ground truth issues using syntactic analysis."""

    def __init__(self):
        self.thresholds = {
            'long_method': 50,  # lines
            'long_class': 300,
            'long_params': 5,
            'magic_number': r'\b\d{2,}\b(?!\s*[=<>!])',  # Exclude small nums
            'high_complexity': 10,  # Cyclomatic complexity
            'deep_nesting': 4,  # Indent levels
            'duplicate_code': 5,  # Min lines for dup
            'hardcoded_secret': r"(password|api_key|secret|token)\s*=\s*['\"][^'\"]+['\"]",
            'dead_code': r"^\s*#.*(TODO|FIXME)|^\s*pass\s*$",
            'missing_docstring': True  # Flag functions without docstrings
        }

    def generate_ground_truth(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        issues = []
        tree = ast.parse(code)
        lines = code.split('\n')

        # Walk AST for structural issues
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                issues.extend(self._check_function(node, code, lines))
            elif isinstance(node, ast.ClassDef):
                issues.extend(self._check_class(node, code, lines))

        # Regex-based patterns
        issues.extend(self._check_patterns(code, lines))

        # Deduplicate
        unique_issues = {f"{i['line']}_{i['type']}": i for i in issues}.values()
        return list(unique_issues)

    def _check_function(self, node: ast.FunctionDef, code: str, lines: List[str]) -> List[Dict]:
        issues = []
        start, end = node.lineno, node.end_lineno
        func_lines = end - start + 1
        if func_lines > self.thresholds['long_method']:
            issues.append(
                {'line': start, 'type': 'long_method', 'description': f'Function {node.name} has {func_lines} lines'})

        param_count = len(node.args.args)
        if param_count > self.thresholds['long_params']:
            issues.append({'line': start, 'type': 'long_params', 'description': f'{param_count} params in {node.name}'})

        complexity = self._calc_complexity(node)
        if complexity > self.thresholds['high_complexity']:
            issues.append(
                {'line': start, 'type': 'high_complexity', 'description': f'Complexity {complexity} in {node.name}'})

        if not ast.get_docstring(node):
            issues.append({'line': start, 'type': 'missing_docstring', 'description': f'No docstring in {node.name}'})

        return issues

    def _check_class(self, node: ast.ClassDef, code: str, lines: List[str]) -> List[Dict]:
        issues = []
        class_lines = node.end_lineno - node.lineno + 1
        if class_lines > self.thresholds['long_class']:
            issues.append({'line': node.lineno, 'type': 'long_class',
                           'description': f'Class {node.name} has {class_lines} lines'})
        return issues

    def _check_patterns(self, code: str, lines: List[str]) -> List[Dict]:
        issues = []
        # Magic numbers
        for line_num, line in enumerate(lines, 1):
            matches = re.findall(self.thresholds['magic_number'], line)
            for match in matches:
                if int(match) not in [0, 1, 2, 10, 100]:
                    issues.append({'line': line_num, 'type': 'magic_number', 'description': f'Magic number {match}'})

        # Hardcoded secrets
        for line_num, line in enumerate(lines, 1):
            if re.search(self.thresholds['hardcoded_secret'], line, re.IGNORECASE):
                issues.append({'line': line_num, 'type': 'hardcoded_secret', 'description': 'Hardcoded secret found'})

        # Dead code
        for line_num, line in enumerate(lines, 1):
            if re.match(self.thresholds['dead_code'], line):
                issues.append({'line': line_num, 'type': 'dead_code', 'description': 'Dead code or TODO/FIXME'})

        # Deep nesting (simple indent count)
        max_indent = max(len(line) - len(line.lstrip()) // 4 for line in lines)
        if max_indent > self.thresholds['deep_nesting']:
            issues.append({'line': 1, 'type': 'deep_nesting', 'description': f'Max nesting depth {max_indent}'})

        return issues

    def _calc_complexity(self, node: ast.AST) -> int:
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity


class CodeAnalysisEvaluator:
    """Runs your agents and computes metrics against ground truth."""

    def __init__(self, agent_functions: List[callable]):
        self.agent_functions = agent_functions  # e.g., [run_quality_agent, run_security_agent, ...]
        self.ground_truth_gen = SyntacticGroundTruthGenerator()

    def evaluate_file(self, file_path: str, api_key: str) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            code = f.read()

        # Step 1: Generate ground truth
        ground_truth = self.ground_truth_gen.generate_ground_truth(code, file_path)

        # Step 2: Run your agents to get predictions
        predictions = []
        for agent_func in self.agent_functions:
            try:
                result = agent_func(code, api_key)
                predictions.extend(result.get('issues', []))
            except Exception as e:
                print(f"Agent failed: {e}")

        # Deduplicate predictions
        unique_preds = {f"{p.get('line', 0)}_{p.get('type', '')}": p for p in predictions}.values()

        # Step 3: Match predictions to ground truth
        tp, fp, fn = self._match_issues(list(unique_preds), ground_truth)

        # Compute metrics
        precision = tp / (tp + fp) if tp + fp > 0 else 0
        recall = tp / (tp + fn) if tp + fn > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0

        return {
            'file': file_path,
            'ground_truth_count': len(ground_truth),
            'prediction_count': len(unique_preds),
            'tp': tp, 'fp': fp, 'fn': fn,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'ground_truth': ground_truth,
            'predictions': list(unique_preds)
        }

    def _match_issues(self, preds: List[Dict], gt: List[Dict]) -> tuple[int, int, int]:
        tp = 0
        matched_gt = set()
        for pred in preds:
            for i, g in enumerate(gt):
                if i in matched_gt:
                    continue
                if pred.get('line') == g.get('line') and pred.get('type') == g.get('type'):
                    tp += 1
                    matched_gt.add(i)
                    break
        fp = len(preds) - tp
        fn = len(gt) - tp
        return tp, fp, fn

# Example usage (add your agents)
# evaluator = CodeAnalysisEvaluator([run_quality_agent, run_security_agent, run_code_smell_agent])
# result = evaluator.evaluate_file('test_data/synthetic/sample_0.py', 'your_api_key')