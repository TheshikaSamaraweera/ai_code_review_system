# agents/code_smell_agent.py
import json
import re
import ast
from typing import List, Dict, Any, Optional
from collections import defaultdict
from llm.gemini_client import init_gemini
from memory.session_memory import remember_issue
from agents.base_agent import BaseAgent


class CodeSmellAgent(BaseAgent):
    """Specialized agent for detecting code smells and anti-patterns."""

    def __init__(self, api_key: str = None):
        super().__init__("CodeSmellAgent")
        self.api_key = api_key
        self.smell_patterns = self._initialize_smell_patterns()

    def _initialize_smell_patterns(self) -> Dict[str, Any]:
        """Initialize patterns for common code smells."""
        return {
            "long_method": {"threshold": 50, "type": "Long Method"},
            "long_class": {"threshold": 300, "type": "Large Class"},
            "long_parameter_list": {"threshold": 5, "type": "Long Parameter List"},
            "duplicate_code": {"threshold": 5, "type": "Duplicate Code"},
            "dead_code": {"patterns": [r"^\s*#.*TODO", r"^\s*#.*FIXME", r"^\s*pass\s*$"], "type": "Dead Code"},
            "magic_numbers": {"pattern": r"\b\d{2,}\b(?!\s*[=<>!])", "type": "Magic Numbers"},
            "god_class": {"threshold": 20, "type": "God Class"},
            "feature_envy": {"threshold": 3, "type": "Feature Envy"},
            "inappropriate_intimacy": {"threshold": 5, "type": "Inappropriate Intimacy"}
        }

    def analyze(self, code: str, language: str = "Python") -> Dict[str, Any]:
        """Analyze code for code smells and anti-patterns."""
        print("👃 Code Smell Agent: Detecting code smells and anti-patterns...")

        issues = []

        if language == "Python":
            # Python-specific analysis using AST
            ast_issues = self._analyze_python_ast(code)
            issues.extend(ast_issues)

        # General pattern-based analysis
        pattern_issues = self._detect_pattern_smells(code, language)
        issues.extend(pattern_issues)

        # Complexity analysis
        complexity_issues = self._analyze_complexity(code, language)
        issues.extend(complexity_issues)

        # AI-based smell detection for nuanced patterns
        ai_issues = self._ai_smell_detection(code, language)
        issues.extend(ai_issues)

        # Deduplicate and sort issues
        issues = self._deduplicate_issues(issues)

        # Calculate code quality score
        score = self._calculate_smell_score(issues)

        # Remember issues
        for issue in issues:
            remember_issue(issue)

        print(f"✅ Code Smell Agent completed - Score: {score}/100, Smells: {len(issues)}")

        return {
            "score": score,
            "issues": issues,
            "summary": self._generate_smell_summary(issues),
            "refactoring_suggestions": self._generate_refactoring_suggestions(issues)
        }

    def _analyze_python_ast(self, code: str) -> List[Dict]:
        """Analyze Python code using AST for structural smells."""
        issues = []

        try:
            tree = ast.parse(code)

            # Analyze classes and methods
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_issues = self._analyze_class(node, code)
                    issues.extend(class_issues)
                elif isinstance(node, ast.FunctionDef):
                    function_issues = self._analyze_function(node, code)
                    issues.extend(function_issues)

            # Detect duplicate code blocks
            duplicate_issues = self._detect_duplicate_code(tree, code)
            issues.extend(duplicate_issues)

        except SyntaxError as e:
            print(f"⚠️ Syntax error in code: {e}")

        return issues

    def _analyze_class(self, class_node: ast.ClassDef, code: str) -> List[Dict]:
        """Analyze a class for code smells."""
        issues = []
        lines = code.split('\n')

        # Check class size
        class_lines = class_node.end_lineno - class_node.lineno + 1
        if class_lines > self.smell_patterns["long_class"]["threshold"]:
            issues.append({
                "line": class_node.lineno,
                "type": "Large Class",
                "severity": "medium",
                "description": f"Class '{class_node.name}' has {class_lines} lines (threshold: {self.smell_patterns['long_class']['threshold']})",
                "suggestion": "Consider breaking this class into smaller, more focused classes",
                "metrics": {"lines": class_lines},
                "confidence": 0.9
            })

        # Check number of methods (God Class detection)
        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) > self.smell_patterns["god_class"]["threshold"]:
            issues.append({
                "line": class_node.lineno,
                "type": "God Class",
                "severity": "high",
                "description": f"Class '{class_node.name}' has {len(methods)} methods (threshold: {self.smell_patterns['god_class']['threshold']})",
                "suggestion": "This class is doing too much. Apply Single Responsibility Principle and split into multiple classes",
                "metrics": {"method_count": len(methods)},
                "confidence": 0.85
            })

        # Check for data class smell (class with only getters/setters)
        getter_setter_count = sum(1 for m in methods if m.name.startswith(('get_', 'set_')))
        if len(methods) > 0 and getter_setter_count / len(methods) > 0.7:
            issues.append({
                "line": class_node.lineno,
                "type": "Data Class",
                "severity": "low",
                "description": f"Class '{class_node.name}' appears to be a data class with mostly getters/setters",
                "suggestion": "Consider using @dataclass decorator or moving behavior to this class",
                "confidence": 0.75
            })

        return issues

    def _analyze_function(self, func_node: ast.FunctionDef, code: str) -> List[Dict]:
        """Analyze a function for code smells."""
        issues = []

        # Check function length
        func_lines = func_node.end_lineno - func_node.lineno + 1
        if func_lines > self.smell_patterns["long_method"]["threshold"]:
            issues.append({
                "line": func_node.lineno,
                "type": "Long Method",
                "severity": "medium",
                "description": f"Function '{func_node.name}' has {func_lines} lines (threshold: {self.smell_patterns['long_method']['threshold']})",
                "suggestion": "Extract smaller functions with single responsibilities",
                "metrics": {"lines": func_lines},
                "confidence": 0.9
            })

        # Check parameter count
        param_count = len(func_node.args.args)
        if param_count > self.smell_patterns["long_parameter_list"]["threshold"]:
            issues.append({
                "line": func_node.lineno,
                "type": "Long Parameter List",
                "severity": "medium",
                "description": f"Function '{func_node.name}' has {param_count} parameters (threshold: {self.smell_patterns['long_parameter_list']['threshold']})",
                "suggestion": "Consider using a parameter object or builder pattern",
                "metrics": {"param_count": param_count},
                "confidence": 0.95
            })

        # Calculate cyclomatic complexity
        complexity = self._calculate_cyclomatic_complexity(func_node)
        if complexity > 10:
            issues.append({
                "line": func_node.lineno,
                "type": "High Complexity",
                "severity": "high" if complexity > 15 else "medium",
                "description": f"Function '{func_node.name}' has cyclomatic complexity of {complexity}",
                "suggestion": "Simplify logic by extracting methods or using polymorphism",
                "metrics": {"complexity": complexity},
                "confidence": 0.9
            })

        return issues

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                complexity += sum(1 for _ in child.ifs) + 1

        return complexity

    def _detect_duplicate_code(self, tree: ast.AST, code: str) -> List[Dict]:
        """Detect duplicate code blocks."""
        issues = []
        code_blocks = defaultdict(list)

        # Extract and hash code blocks
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.For, ast.While, ast.If)):
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    block_lines = code.split('\n')[node.lineno - 1:node.end_lineno]
                    block_str = '\n'.join(block_lines).strip()

                    # Normalize whitespace for comparison
                    normalized = re.sub(r'\s+', ' ', block_str)
                    if len(normalized) > 50:  # Only consider substantial blocks
                        code_blocks[normalized].append(node.lineno)

        # Find duplicates
        for block_str, line_numbers in code_blocks.items():
            if len(line_numbers) > 1:
                issues.append({
                    "line": line_numbers[0],
                    "type": "Duplicate Code",
                    "severity": "medium",
                    "description": f"Similar code blocks found at lines: {', '.join(map(str, line_numbers))}",
                    "suggestion": "Extract duplicate code into a reusable function",
                    "metrics": {"occurrences": len(line_numbers)},
                    "confidence": 0.8
                })

        return issues

    def _detect_pattern_smells(self, code: str, language: str) -> List[Dict]:
        """Detect code smells using regex patterns."""
        issues = []
        lines = code.split('\n')

        # Check for magic numbers
        magic_pattern = self.smell_patterns["magic_numbers"]["pattern"]
        for line_num, line in enumerate(lines, 1):
            # Skip comments and strings
            if not line.strip().startswith('#') and not line.strip().startswith(('"""', "'''")):
                matches = re.findall(magic_pattern, line)
                for match in matches:
                    if int(match) not in [0, 1, 2, 10, 100]:  # Common acceptable numbers
                        issues.append({
                            "line": line_num,
                            "type": "Magic Number",
                            "severity": "low",
                            "description": f"Magic number {match} found",
                            "suggestion": f"Extract {match} to a named constant",
                            "confidence": 0.7
                        })

        # Check for commented-out code
        commented_code_lines = []
        for line_num, line in enumerate(lines, 1):
            if re.match(r'^\s*#\s*\w+.*[({]', line):  # Likely commented code
                commented_code_lines.append(line_num)

        if len(commented_code_lines) > 5:
            issues.append({
                "line": commented_code_lines[0],
                "type": "Commented Code",
                "severity": "low",
                "description": f"Large blocks of commented code found ({len(commented_code_lines)} lines)",
                "suggestion": "Remove commented code and use version control for history",
                "metrics": {"lines": len(commented_code_lines)},
                "confidence": 0.6
            })

        return issues

    def _analyze_complexity(self, code: str, language: str) -> List[Dict]:
        """Analyze code complexity metrics."""
        issues = []

        # Check nesting depth
        max_nesting = self._calculate_max_nesting(code)
        if max_nesting > 4:
            issues.append({
                "line": 1,
                "type": "Deep Nesting",
                "severity": "medium",
                "description": f"Maximum nesting depth of {max_nesting} detected",
                "suggestion": "Refactor nested conditions using guard clauses or extract methods",
                "metrics": {"max_depth": max_nesting},
                "confidence": 0.85
            })

        return issues

    def _calculate_max_nesting(self, code: str) -> int:
        """Calculate maximum nesting depth in code."""
        lines = code.split('\n')
        max_depth = 0
        current_depth = 0

        for line in lines:
            # Simple indentation-based nesting detection
            indent = len(line) - len(line.lstrip())
            if indent > 0:
                depth = indent // 4  # Assuming 4-space indentation
                max_depth = max(max_depth, depth)

        return max_depth

    def _ai_smell_detection(self, code: str, language: str) -> List[Dict]:
        """Use AI to detect complex code smells."""
        try:
            gemini = init_gemini()

            prompt = self._generate_smell_prompt(code, language)
            response = gemini.generate_content(prompt)

            # Parse response
            json_str = response.text.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[-1].split("```")[0].strip()

            result = json.loads(json_str)
            issues = result.get("code_smells", [])

            # Normalize issues
            for issue in issues:
                issue["source"] = "ai"
                issue.setdefault("confidence", 0.75)

            return issues

        except Exception as e:
            print(f"⚠️ AI smell detection failed: {e}")
            return []

    def _generate_smell_prompt(self, code: str, language: str) -> str:
        """Generate prompt for AI smell detection."""
        return f"""You are a senior software architect specialized in identifying code smells and anti-patterns in {language} code.

Analyze the following code for these code smells:
1. Long Method/Function
2. Large Class
3. Feature Envy
4. Data Clumps
5. Primitive Obsession
6. Switch Statements (use of long if-else chains)
7. Parallel Inheritance Hierarchies
8. Lazy Class
9. Speculative Generality
10. Temporary Field
11. Message Chains
12. Middle Man
13. Inappropriate Intimacy
14. Alternative Classes with Different Interfaces
15. Incomplete Library Class
16. Refused Bequest
17. Comments (excessive or unnecessary)

Return a JSON object:
{{
  "code_smells": [
    {{
      "line": <line_number>,
      "type": "<smell_type>",
      "severity": "high|medium|low",
      "description": "<detailed_description>",
      "suggestion": "<refactoring_suggestion>",
      "pattern": "<anti_pattern_name_if_applicable>"
    }}
  ],
  "design_improvements": [
    "<design_improvement_suggestion>"
  ]
}}

CODE:
```{language.lower()}
{code}
```"""

    def _deduplicate_issues(self, issues: List[Dict]) -> List[Dict]:
        """Remove duplicate issues."""
        seen = set()
        unique_issues = []

        for issue in issues:
            key = (issue.get("line", 0), issue.get("type", ""))
            if key not in seen:
                seen.add(key)
                unique_issues.append(self._normalize_smell_issue(issue))

        # Sort by severity and line
        severity_order = {"high": 0, "medium": 1, "low": 2}
        unique_issues.sort(key=lambda x: (severity_order.get(x["severity"], 1), x.get("line", 0)))

        return unique_issues

    def _normalize_smell_issue(self, issue: Dict) -> Dict:
        """Normalize issue format."""
        return {
            "line": issue.get("line", 0),
            "type": issue.get("type", "Code Smell"),
            "severity": issue.get("severity", "medium"),
            "description": issue.get("description", ""),
            "suggestion": issue.get("suggestion", "Refactor this code"),
            "metrics": issue.get("metrics", {}),
            "confidence": issue.get("confidence", 0.7),
            "source": issue.get("source", "code_smell_agent"),
            "category": "code_smell"
        }

    def _calculate_smell_score(self, issues: List[Dict]) -> float:
        """Calculate code quality score based on smells."""
        if not issues:
            return 100.0

        severity_weights = {
            "high": 10,
            "medium": 5,
            "low": 2
        }

        total_penalty = 0
        for issue in issues:
            penalty = severity_weights.get(issue["severity"], 3)
            confidence = issue.get("confidence", 0.7)
            total_penalty += penalty * confidence

        # More lenient scoring for code smells
        total_penalty = min(total_penalty * 0.8, 100)

        return max(0, 100 - total_penalty)

    def _generate_smell_summary(self, issues: List[Dict]) -> Dict:
        """Generate summary of code smell findings."""
        smell_types = defaultdict(int)
        for issue in issues:
            smell_types[issue["type"]] += 1

        return {
            "total_smells": len(issues),
            "smell_distribution": dict(smell_types),
            "most_common": max(smell_types.items(), key=lambda x: x[1])[0] if smell_types else None,
            "high_severity": len([i for i in issues if i["severity"] == "high"]),
            "medium_severity": len([i for i in issues if i["severity"] == "medium"]),
            "low_severity": len([i for i in issues if i["severity"] == "low"])
        }

    def _generate_refactoring_suggestions(self, issues: List[Dict]) -> List[str]:
        """Generate prioritized refactoring suggestions based on smells."""
        suggestions = []
        smell_counts = defaultdict(int)

        for issue in issues:
            smell_counts[issue["type"]] += 1

        # Priority refactoring suggestions
        if smell_counts.get("God Class", 0) > 0:
            suggestions.append("🎯 Priority: Break down large classes using Single Responsibility Principle")

        if smell_counts.get("Long Method", 0) > 2:
            suggestions.append("📐 Extract methods to reduce complexity and improve readability")

        if smell_counts.get("Duplicate Code", 0) > 0:
            suggestions.append("♻️ Apply DRY principle - extract duplicate code into reusable functions")

        if smell_counts.get("High Complexity", 0) > 0:
            suggestions.append("🔀 Simplify complex logic using guard clauses or strategy pattern")

        if smell_counts.get("Feature Envy", 0) > 0:
            suggestions.append("🔄 Move methods closer to the data they operate on")

        if smell_counts.get("Data Class", 0) > 0:
            suggestions.append("💡 Add behavior to data classes or use proper encapsulation")

        if smell_counts.get("Magic Number", 0) > 3:
            suggestions.append("🔢 Extract magic numbers to named constants for clarity")

        if not suggestions:
            suggestions.append("✅ Code structure is generally good - focus on minor improvements")

        return suggestions


def run_code_smell_agent(code: str, api_key: str = None, language: str = "Python") -> Dict[str, Any]:
    """Convenience function to run code smell analysis."""
    agent = CodeSmellAgent(api_key)
    return agent.analyze(code, language)