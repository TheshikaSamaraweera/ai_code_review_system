# agents/security_agent.py
import json
import re
from typing import List, Dict, Any
from llm.gemini_client import init_gemini
from memory.session_memory import remember_issue
from agents.base_agent import BaseAgent


class SecurityAgent(BaseAgent):
    """Specialized agent for detecting security vulnerabilities and risks."""

    def __init__(self, api_key: str = None):
        super().__init__("SecurityAgent")
        self.api_key = api_key
        self.vulnerability_patterns = self._load_vulnerability_patterns()

    def _load_vulnerability_patterns(self) -> Dict[str, List[Dict]]:
        """Load common vulnerability patterns for quick detection."""
        return {
            "Python": [
                {
                    "pattern": r"eval\s*\(",
                    "type": "Code Injection",
                    "severity": "critical",
                    "description": "Use of eval() can lead to code injection attacks"
                },
                {
                    "pattern": r"exec\s*\(",
                    "type": "Code Injection",
                    "severity": "critical",
                    "description": "Use of exec() can lead to code injection attacks"
                },
                {
                    "pattern": r"__import__\s*\(",
                    "type": "Dynamic Import",
                    "severity": "high",
                    "description": "Dynamic imports can be a security risk"
                },
                {
                    "pattern": r"pickle\.loads?\s*\(",
                    "type": "Deserialization",
                    "severity": "high",
                    "description": "Pickle deserialization of untrusted data is dangerous"
                },
                {
                    "pattern": r"os\.system\s*\(",
                    "type": "Command Injection",
                    "severity": "high",
                    "description": "os.system() is vulnerable to command injection"
                },
                {
                    "pattern": r"subprocess\.(call|run|Popen)\s*\([^,]*shell\s*=\s*True",
                    "type": "Command Injection",
                    "severity": "high",
                    "description": "Shell=True in subprocess is vulnerable to injection"
                },
                {
                    "pattern": r"(password|api_key|secret|token)\s*=\s*['\"][^'\"]+['\"]",
                    "type": "Hardcoded Secrets",
                    "severity": "high",
                    "description": "Hardcoded secrets detected"
                },
                {
                    "pattern": r"verify\s*=\s*False",
                    "type": "SSL Verification",
                    "severity": "medium",
                    "description": "SSL certificate verification disabled"
                },
                {
                    "pattern": r"debug\s*=\s*True",
                    "type": "Debug Mode",
                    "severity": "medium",
                    "description": "Debug mode enabled in production code"
                }
            ],
            "JavaScript": [
                {
                    "pattern": r"eval\s*\(",
                    "type": "Code Injection",
                    "severity": "critical",
                    "description": "eval() usage can lead to code injection"
                },
                {
                    "pattern": r"innerHTML\s*=",
                    "type": "XSS Risk",
                    "severity": "high",
                    "description": "innerHTML can lead to XSS vulnerabilities"
                },
                {
                    "pattern": r"document\.write\s*\(",
                    "type": "XSS Risk",
                    "severity": "high",
                    "description": "document.write() can lead to XSS"
                },
                {
                    "pattern": r"new\s+Function\s*\(",
                    "type": "Code Injection",
                    "severity": "high",
                    "description": "Function constructor can execute arbitrary code"
                }
            ]
        }

    def analyze(self, code: str, language: str = "Python") -> Dict[str, Any]:
        """Analyze code for security vulnerabilities."""
        print("🔒 Security Agent: Analyzing for vulnerabilities...")

        # Quick pattern-based detection
        pattern_issues = self._detect_pattern_vulnerabilities(code, language)

        # AI-based deep analysis
        ai_issues = self._ai_security_analysis(code, language)

        # Merge and deduplicate issues
        all_issues = self._merge_security_issues(pattern_issues, ai_issues)

        # Calculate security score
        score = self._calculate_security_score(all_issues)

        # Remember issues in session memory
        for issue in all_issues:
            remember_issue(issue)

        print(f"✅ Security Agent completed - Score: {score}/100, Issues: {len(all_issues)}")

        return {
            "score": score,
            "issues": all_issues,
            "summary": self._generate_security_summary(all_issues)
        }

    def _detect_pattern_vulnerabilities(self, code: str, language: str) -> List[Dict]:
        """Detect vulnerabilities using regex patterns."""
        issues = []
        patterns = self.vulnerability_patterns.get(language, [])

        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            for vuln_pattern in patterns:
                if re.search(vuln_pattern["pattern"], line, re.IGNORECASE):
                    issues.append({
                        "line": line_num,
                        "type": vuln_pattern["type"],
                        "severity": vuln_pattern["severity"],
                        "description": vuln_pattern["description"],
                        "code_snippet": line.strip(),
                        "source": "pattern",
                        "confidence": 0.95
                    })

        return issues

    def _ai_security_analysis(self, code: str, language: str) -> List[Dict]:
        """Use AI to detect complex security vulnerabilities."""
        try:
            gemini = init_gemini()

            prompt = self._generate_security_prompt(code, language)
            response = gemini.generate_content(prompt)

            # Parse AI response
            json_str = response.text.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[-1].split("```")[0].strip()

            result = json.loads(json_str)
            issues = result.get("security_issues", [])

            # Normalize AI issues
            for issue in issues:
                issue["source"] = "ai"
                issue.setdefault("confidence", 0.85)
                issue.setdefault("type", "Security Vulnerability")

            return issues

        except Exception as e:
            print(f"⚠️ AI security analysis failed: {e}")
            return []

    def _generate_security_prompt(self, code: str, language: str) -> str:
        """Generate prompt for AI security analysis."""
        return f"""You are a senior security engineer specializing in {language} code security.
Analyze the following code for security vulnerabilities, focusing on:

1. Injection vulnerabilities (SQL, Command, Code injection)
2. Authentication and authorization issues
3. Sensitive data exposure
4. Security misconfigurations
5. Cross-site scripting (XSS) risks
6. Insecure deserialization
7. Using components with known vulnerabilities
8. Insufficient logging and monitoring
9. Broken access control
10. Security through obscurity

Return a JSON object with:
{{
  "security_issues": [
    {{
      "line": <line_number>,
      "type": "<vulnerability_type>",
      "severity": "critical|high|medium|low",
      "description": "<detailed_description>",
      "impact": "<potential_impact>",
      "suggestion": "<how_to_fix>",
      "cwe_id": "<CWE_ID_if_applicable>",
      "owasp_category": "<OWASP_category_if_applicable>"
    }}
  ],
  "security_best_practices": [
    "<best_practice_recommendation>"
  ]
}}

CODE TO ANALYZE:
```{language.lower()}
{code}
```"""

    def _merge_security_issues(self, pattern_issues: List[Dict], ai_issues: List[Dict]) -> List[Dict]:
        """Merge and deduplicate security issues from different sources."""
        all_issues = []
        seen = set()

        # Process pattern issues first (higher confidence)
        for issue in pattern_issues:
            key = (issue["line"], issue["type"])
            if key not in seen:
                seen.add(key)
                all_issues.append(self._normalize_issue(issue))

        # Add AI issues that don't duplicate pattern issues
        for issue in ai_issues:
            key = (issue.get("line", 0), issue.get("type", ""))
            if key not in seen:
                seen.add(key)
                all_issues.append(self._normalize_issue(issue))

        # Sort by severity and line number
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_issues.sort(key=lambda x: (severity_order.get(x["severity"], 2), x.get("line", 0)))

        return all_issues

    def _normalize_issue(self, issue: Dict) -> Dict:
        """Normalize issue format."""
        return {
            "line": issue.get("line", 0),
            "type": issue.get("type", "Security Issue"),
            "severity": issue.get("severity", "medium"),
            "description": issue.get("description", ""),
            "suggestion": issue.get("suggestion", "Review and fix this security issue"),
            "impact": issue.get("impact", ""),
            "confidence": issue.get("confidence", 0.8),
            "source": issue.get("source", "security_agent"),
            "category": "security"
        }

    def _calculate_security_score(self, issues: List[Dict]) -> float:
        """Calculate security score based on issues found."""
        if not issues:
            return 100.0

        severity_weights = {
            "critical": 25,
            "high": 15,
            "medium": 8,
            "low": 3
        }

        total_penalty = 0
        for issue in issues:
            penalty = severity_weights.get(issue["severity"], 5)
            confidence = issue.get("confidence", 0.8)
            total_penalty += penalty * confidence

        # Cap penalty at 100
        total_penalty = min(total_penalty, 100)

        return max(0, 100 - total_penalty)

    def _generate_security_summary(self, issues: List[Dict]) -> Dict:
        """Generate a summary of security findings."""
        summary = {
            "total_issues": len(issues),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "top_risks": [],
            "recommendations": []
        }

        for issue in issues:
            severity = issue["severity"]
            summary[severity] = summary.get(severity, 0) + 1

        # Identify top risks
        critical_and_high = [i for i in issues if i["severity"] in ["critical", "high"]]
        summary["top_risks"] = critical_and_high[:3]

        # Generate recommendations
        if summary["critical"] > 0:
            summary["recommendations"].append("🔴 URGENT: Address critical security vulnerabilities immediately")
        if summary["high"] > 0:
            summary["recommendations"].append("⚠️ Fix high-severity security issues before deployment")
        if any("hardcoded" in i.get("description", "").lower() for i in issues):
            summary["recommendations"].append("🔑 Move secrets to environment variables or secure vaults")
        if any("injection" in i.get("type", "").lower() for i in issues):
            summary["recommendations"].append("💉 Implement input validation and parameterized queries")

        return summary


def run_security_agent(code: str, api_key: str = None, language: str = "Python") -> Dict[str, Any]:
    """Convenience function to run security analysis."""
    agent = SecurityAgent(api_key)
    return agent.analyze(code, language)