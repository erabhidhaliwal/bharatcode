"""
Expert-Level Code Reviewer
Advanced code analysis, quality metrics, auto-improvement, and learning
"""

import os
import json
from typing import Dict, List, Tuple
from datetime import datetime
from brain.router import route_chat


EXPERT_REVIEWER_PROMPT = """You are an EXPERT CODE REVIEWER and quality architect.

Review this code comprehensively:

{code_content}

EVALUATION FRAMEWORK:
1. CORRECTNESS
   - Logic correctness
   - Edge case handling
   - Error handling
   - Input validation

2. PERFORMANCE
   - Time complexity
   - Space complexity
   - Bottlenecks
   - Optimization opportunities

3. MAINTAINABILITY
   - Code clarity
   - Naming conventions
   - DRY principle
   - SOLID principles

4. SECURITY
   - Vulnerability identification
   - Input validation
   - Authentication/Authorization
   - Data protection

5. SCALABILITY
   - Horizontal scalability
   - Caching opportunities
   - Database design
   - Architecture patterns

6. ARCHITECTURE
   - Design patterns
   - Separation of concerns
   - Modularity
   - API design

PROVIDE DETAILED FEEDBACK:
{{
  "overall_quality_score": 0-100,
  "categories": {{
    "correctness": {{"score": 0-100, "issues": []}},
    "performance": {{"score": 0-100, "issues": []}},
    "maintainability": {{"score": 0-100, "issues": []}},
    "security": {{"score": 0-100, "issues": []}},
    "scalability": {{"score": 0-100, "issues": []}},
    "architecture": {{"score": 0-100, "issues": []}}
  }},
  "critical_issues": [
    {{
      "issue": "description",
      "severity": "critical|high|medium|low",
      "location": "file:line",
      "impact": "what happens if not fixed",
      "solution": "how to fix"
    }}
  ],
  "improvements": [
    {{
      "category": "which category",
      "suggestion": "what to improve",
      "reasoning": "why",
      "example": "code example"
    }}
  ],
  "patterns_applied": ["pattern1", "pattern2"],
  "anti_patterns_found": ["antipattern1"],
  "testing_recommendations": ["test1", "test2"],
  "documentation_gaps": ["gap1", "gap2"]
}}"""


IMPROVEMENT_SUGGESTION_PROMPT = """Generate specific code improvement for:

{code_section}

Problem: {problem}
Context: {context}

Provide:
1. Improved code
2. Explanation of changes
3. Benefits
4. Potential concerns
5. Testing strategy

Return as JSON."""


REFACTORING_PROPOSAL_PROMPT = """Create detailed refactoring proposal:

Current Code:
{current_code}

Goals: {refactoring_goals}

Provide:
{{
  "refactoring_strategy": "overall approach",
  "phases": [
    {{
      "phase": "name",
      "changes": ["change1"],
      "risk": "low|medium|high",
      "testing": ["test1"],
      "rollback_plan": "how to revert"
    }}
  ],
  "new_code": "refactored code",
  "migration_guide": "how to migrate",
  "before_after_metrics": {{
    "lines_of_code": {"before": 0, "after": 0},
    "cyclomatic_complexity": {"before": 0, "after": 0},
    "test_coverage": {"before": "0%", "after": "0%"}
  }}
}}"""


class ExpertReviewer:
    """Expert code reviewer with advanced analysis"""

    def __init__(self, model=None):
        self.model = model or os.getenv("REVIEWER_MODEL") or os.getenv("DEFAULT_MODEL")
        self.review_history = []
        self.improvement_suggestions = {}

    def review_code(self, code_content: str, context: str = "") -> Dict:
        """Perform expert code review"""
        response = route_chat(
            [
                {"role": "system", "content": "You are an expert code reviewer."},
                {
                    "role": "user",
                    "content": EXPERT_REVIEWER_PROMPT.format(code_content=code_content),
                },
            ],
            model=self.model,
        )

        review = self._parse_review(response)

        self.review_history.append({
            "timestamp": datetime.now().isoformat(),
            "code_hash": hash(code_content),
            "review": review,
            "context": context,
        })

        return review

    def suggest_improvements(self, code_section: str, problem: str, context: str = "") -> Dict:
        """Suggest specific improvements"""
        response = route_chat(
            [
                {
                    "role": "system",
                    "content": "You are an expert code improvement specialist.",
                },
                {
                    "role": "user",
                    "content": IMPROVEMENT_SUGGESTION_PROMPT.format(
                        code_section=code_section,
                        problem=problem,
                        context=context,
                    ),
                },
            ],
            model=self.model,
        )

        return self._parse_json(response)

    def propose_refactoring(
        self, current_code: str, goals: str
    ) -> Dict:
        """Propose comprehensive refactoring"""
        response = route_chat(
            [
                {
                    "role": "system",
                    "content": "You are a refactoring expert.",
                },
                {
                    "role": "user",
                    "content": REFACTORING_PROPOSAL_PROMPT.format(
                        current_code=current_code,
                        refactoring_goals=goals,
                    ),
                },
            ],
            model=self.model,
        )

        return self._parse_json(response)

    def analyze_performance(self, code_content: str) -> Dict:
        """Analyze performance characteristics"""
        prompt = f"""Analyze performance characteristics of this code:

{code_content}

Provide:
{{
  "time_complexity": "O(n), etc",
  "space_complexity": "O(n), etc",
  "bottlenecks": ["bottleneck1"],
  "optimization_opportunities": [
    {{
      "optimization": "description",
      "impact": "performance improvement",
      "effort": "easy|medium|hard"
    }}
  ],
  "benchmarking_strategy": "how to measure",
  "caching_opportunities": ["opportunity1"],
  "parallelization_potential": "description"
}}"""

        response = route_chat(
            [
                {"role": "system", "content": "You are a performance analyst."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return self._parse_json(response)

    def check_security(self, code_content: str) -> Dict:
        """Perform security analysis"""
        prompt = f"""Security audit of this code:

{code_content}

Check for:
- Input validation
- SQL injection
- XSS vulnerabilities
- Authentication/Authorization
- Cryptography issues
- Dependency vulnerabilities
- Error handling leaks
- OWASP Top 10

Return:
{{
  "vulnerabilities": [
    {{
      "type": "vulnerability type",
      "severity": "critical|high|medium|low",
      "location": "code location",
      "description": "what's wrong",
      "exploit_scenario": "how it could be exploited",
      "fix": "how to fix it",
      "cwe": "CWE-xxx"
    }}
  ],
  "security_score": 0-100,
  "recommendations": ["recommendation1"]
}}"""

        response = route_chat(
            [
                {"role": "system", "content": "You are a security expert."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return self._parse_json(response)

    def generate_tests(self, code_content: str) -> Dict:
        """Generate comprehensive test cases"""
        prompt = f"""Generate test cases for this code:

{code_content}

Provide:
{{
  "unit_tests": [
    {{
      "test_name": "name",
      "test_code": "code",
      "expected_result": "result"
    }}
  ],
  "edge_cases": ["edge case 1"],
  "integration_tests": ["test 1"],
  "performance_tests": ["test 1"],
  "coverage_target": "percentage",
  "test_framework": "recommended framework"
}}"""

        response = route_chat(
            [
                {"role": "system", "content": "You are a testing expert."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return self._parse_json(response)

    def calculate_metrics(self, code_content: str) -> Dict:
        """Calculate code quality metrics"""
        lines = code_content.split("\n")
        non_comment_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]

        metrics = {
            "total_lines": len(lines),
            "code_lines": len(non_comment_lines),
            "comment_lines": len([l for l in lines if l.strip().startswith("#")]),
            "blank_lines": len([l for l in lines if not l.strip()]),
            "average_line_length": sum(len(l) for l in lines) / max(len(lines), 1),
            "max_line_length": max(len(l) for l in lines) if lines else 0,
        }

        # Function complexity estimation
        functions = code_content.count("def ") + code_content.count("function ")
        classes = code_content.count("class ")
        conditionals = (
            code_content.count("if ") + code_content.count("else") +
            code_content.count("elif") + code_content.count("switch")
        )

        metrics.update({
            "functions": functions,
            "classes": classes,
            "conditionals": conditionals,
            "estimated_complexity": min(conditionals + 1, 10),
        })

        return metrics

    def _parse_review(self, response: str) -> Dict:
        """Parse review response"""
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass

        return {"raw_review": response, "parsed": False}

    def _parse_json(self, response: str):
        """Parse JSON response"""
        try:
            start = response.find("{")
            if start >= 0:
                end = response.rfind("}") + 1
                return json.loads(response[start:end])

            start = response.find("[")
            if start >= 0:
                end = response.rfind("]") + 1
                return json.loads(response[start:end])
        except:
            pass

        return {"raw": response, "parsed": False}


class ContinuousImprover:
    """Continuously improve code based on reviews"""

    def __init__(self):
        self.reviewer = ExpertReviewer()
        self.improvement_log = []
        self.quality_history = []

    def iterative_improvement(self, code: str, iterations: int = 3) -> Dict:
        """Iteratively improve code"""
        current_code = code
        improvements = []

        for i in range(iterations):
            review = self.reviewer.review_code(current_code)
            metrics = self.reviewer.calculate_metrics(current_code)

            self.quality_history.append({
                "iteration": i,
                "metrics": metrics,
                "score": review.get("overall_quality_score", 0),
            })

            if review.get("critical_issues"):
                suggestion = self.reviewer.suggest_improvements(
                    current_code,
                    f"Fix critical issues: {review['critical_issues'][0]['issue']}",
                )

                improvements.append({
                    "iteration": i,
                    "issues_fixed": len(review.get("critical_issues", [])),
                    "suggestion": suggestion,
                })

        return {
            "initial_score": self.quality_history[0]["score"] if self.quality_history else 0,
            "final_score": self.quality_history[-1]["score"] if self.quality_history else 0,
            "improvements": improvements,
            "quality_trend": [h["score"] for h in self.quality_history],
        }

    def generate_improvement_report(self, reviews: List[Dict]) -> Dict:
        """Generate improvement report"""
        return {
            "total_reviews": len(reviews),
            "average_score": sum(r.get("overall_quality_score", 0) for r in reviews) / max(len(reviews), 1),
            "common_issues": self._extract_common_issues(reviews),
            "improvement_areas": self._rank_improvements(reviews),
            "trends": self._analyze_trends(reviews),
        }

    def _extract_common_issues(self, reviews: List[Dict]) -> List[str]:
        """Extract common issues"""
        issues = {}
        for review in reviews:
            for issue in review.get("critical_issues", []):
                issue_type = issue.get("issue", "unknown")
                issues[issue_type] = issues.get(issue_type, 0) + 1

        return sorted(issues.items(), key=lambda x: x[1], reverse=True)

    def _rank_improvements(self, reviews: List[Dict]) -> List[Dict]:
        """Rank improvement opportunities"""
        improvements = {}
        for review in reviews:
            for improvement in review.get("improvements", []):
                category = improvement.get("category", "general")
                if category not in improvements:
                    improvements[category] = 0
                improvements[category] += 1

        return [
            {"category": k, "frequency": v}
            for k, v in sorted(improvements.items(), key=lambda x: x[1], reverse=True)
        ]

    def _analyze_trends(self, reviews: List[Dict]) -> Dict:
        """Analyze quality trends"""
        if not reviews:
            return {}

        scores = [r.get("overall_quality_score", 0) for r in reviews]
        return {
            "trend": "improving" if scores[-1] > scores[0] else "declining",
            "total_improvement": scores[-1] - scores[0],
            "average_score": sum(scores) / len(scores),
            "highest_score": max(scores),
            "lowest_score": min(scores),
        }


def create_expert_reviewer(model=None):
    """Factory for expert reviewer"""
    return ExpertReviewer(model)


def review_code(code_content: str, model=None) -> Dict:
    """Review code"""
    reviewer = ExpertReviewer(model)
    return reviewer.review_code(code_content)
