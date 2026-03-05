"""
Expert Executor
Intelligent command execution, code generation, and optimization
"""

import os
from typing import Dict, Optional
from brain.router import route_chat


EXPERT_EXECUTOR_PROMPT = """You are an EXPERT EXECUTOR - a senior engineer executing complex tasks.

Your execution style:
- Write production-ready code
- Handle edge cases
- Implement error handling
- Add logging and monitoring
- Consider performance
- Ensure security
- Follow best practices

Task: {task}
Context: {context}

Generate code or commands that are:
1. Complete and functional
2. Well-structured and maintainable
3. Secure and performant
4. Well-commented
5. Ready for production

Format response as:
ACTION: <CODE|COMMAND|REFACTOR|ANALYSIS>

For CODE action:
LANGUAGE: <python|javascript|go|rust|java>
FILENAME: path/to/file
```language
[complete, production-ready code]
```

For COMMAND action:
COMMAND: [safe shell command]
TIMEOUT: seconds
EXPLANATION: why this command

For REFACTOR action:
CHANGES: [list of changes]
[refactored code in blocks]

For ANALYSIS action:
ANALYSIS: [detailed analysis]"""


class ExpertExecutor:
    """Expert code executor"""

    def __init__(self, model=None, project_dir=None):
        self.model = model or os.getenv("EXECUTOR_MODEL") or os.getenv("DEFAULT_MODEL")
        self.project_dir = project_dir
        self.execution_history = []

    def execute_task(self, task: str, context: str = "") -> Dict:
        """Execute complex task"""
        prompt = EXPERT_EXECUTOR_PROMPT.format(task=task, context=context)

        response = route_chat(
            [
                {"role": "system", "content": "You are an expert code executor."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        self.execution_history.append({
            "task": task,
            "response": response,
        })

        return self._parse_execution_response(response)

    def generate_code(
        self,
        specification: str,
        language: str = "python",
        context: str = "",
    ) -> Dict:
        """Generate production-ready code"""
        prompt = f"""Generate production-ready {language} code for:

{specification}

Context: {context}

Code requirements:
- Complete and functional
- Error handling
- Type hints/annotations
- Docstrings
- Following language best practices
- Secure
- Performant
- Well-structured

Return the code with explanation."""

        response = route_chat(
            [
                {"role": "system", "content": f"You are expert {language} developer."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return self._parse_code_response(response, language)

    def optimize_code(self, code: str, optimization_goals: str) -> Dict:
        """Optimize existing code"""
        prompt = f"""Optimize this code:

{code}

Optimization goals:
{optimization_goals}

Provide:
1. Optimized code
2. Changes made
3. Performance improvements
4. Trade-offs
5. Benchmarking strategy"""

        response = route_chat(
            [
                {"role": "system", "content": "You are code optimization expert."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return self._parse_optimization_response(response)

    def debug_code(self, code: str, error: str, context: str = "") -> Dict:
        """Debug code issues"""
        prompt = f"""Debug this code:

Code:
{code}

Error/Issue:
{error}

Context: {context}

Provide:
1. Root cause analysis
2. Fixed code
3. Explanation
4. Prevention strategies
5. Test cases"""

        response = route_chat(
            [
                {"role": "system", "content": "You are debugging expert."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return {"debugging": response}

    def create_tests(
        self,
        code: str,
        test_type: str = "unit",
        language: str = "python",
    ) -> Dict:
        """Create comprehensive tests"""
        prompt = f"""Create {test_type} tests for this {language} code:

{code}

Test framework: [appropriate for {language}]

Include:
- Happy path tests
- Edge case tests
- Error condition tests
- Performance tests (if applicable)
- Test documentation

Make tests production-ready."""

        response = route_chat(
            [
                {"role": "system", "content": f"You are {language} testing expert."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return {"tests": response}

    def document_code(self, code: str, detail_level: str = "comprehensive") -> Dict:
        """Generate documentation"""
        prompt = f"""Create {detail_level} documentation for:

{code}

Include:
- Overview/purpose
- Architecture
- API documentation
- Usage examples
- Configuration
- Troubleshooting
- Contributing guide (if applicable)

Format as markdown."""

        response = route_chat(
            [
                {"role": "system", "content": "You are documentation expert."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return {"documentation": response}

    def design_architecture(self, requirements: str) -> Dict:
        """Design system architecture"""
        prompt = f"""Design architecture for:

{requirements}

Provide:
1. System design diagram (as text)
2. Component breakdown
3. Data flow
4. Technology recommendations
5. Scalability strategy
6. Security architecture
7. Deployment strategy
8. Monitoring strategy

Make it production-grade."""

        response = route_chat(
            [
                {"role": "system", "content": "You are solution architect."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return {"architecture": response}

    def create_deployment_plan(self, application: str, platforms: str) -> Dict:
        """Create deployment plan"""
        prompt = f"""Create deployment plan for:

Application: {application}
Target platforms: {platforms}

Include:
- Infrastructure requirements
- Deployment steps
- Configuration management
- Monitoring setup
- Backup strategy
- Disaster recovery
- Rollback procedure
- Load balancing
- Security hardening
- Performance tuning

Make it production-ready."""

        response = route_chat(
            [
                {"role": "system", "content": "You are DevOps expert."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return {"deployment_plan": response}

    def create_cicd_pipeline(self, project_type: str, technology_stack: str) -> Dict:
        """Create CI/CD pipeline configuration"""
        prompt = f"""Create CI/CD pipeline for:

Project type: {project_type}
Technology stack: {technology_stack}

Include:
- Build steps
- Testing automation
- Code quality checks
- Security scanning
- Artifact creation
- Deployment stages
- Monitoring integration
- Notification setup

Provide configurations for popular CI/CD tools."""

        response = route_chat(
            [
                {"role": "system", "content": "You are CI/CD expert."},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )

        return {"cicd_pipeline": response}

    def _parse_execution_response(self, response: str) -> Dict:
        """Parse execution response"""
        if "ACTION: CODE" in response.upper():
            return self._parse_code_response(response)
        elif "ACTION: COMMAND" in response.upper():
            return self._parse_command_response(response)
        elif "ACTION: REFACTOR" in response.upper():
            return self._parse_refactor_response(response)
        else:
            return {"raw": response}

    def _parse_code_response(self, response: str, language: str = "") -> Dict:
        """Parse code response"""
        import re

        pattern = rf"```{language}?\n(.*?)\n```"
        matches = re.findall(pattern, response, re.DOTALL)

        if matches:
            return {
                "code": matches[0],
                "language": language or self._detect_language(matches[0]),
            }

        return {"raw": response}

    def _parse_command_response(self, response: str) -> Dict:
        """Parse command response"""
        if "COMMAND:" in response:
            cmd_start = response.find("COMMAND:") + 8
            cmd_end = response.find("\n", cmd_start)
            command = response[cmd_start:cmd_end].strip()
            return {"command": command}

        return {"raw": response}

    def _parse_refactor_response(self, response: str) -> Dict:
        """Parse refactoring response"""
        return {"refactoring": response}

    def _parse_optimization_response(self, response: str) -> Dict:
        """Parse optimization response"""
        return {"optimization": response}

    def _detect_language(self, code: str) -> str:
        """Detect programming language from code"""
        indicators = {
            "python": ["def ", "import ", "class "],
            "javascript": ["function ", "const ", "async ", "=>"],
            "java": ["public class ", "public static ", "package "],
            "go": ["package ", "func ", "import ("],
            "rust": ["fn ", "impl ", "trait "],
        }

        for lang, keywords in indicators.items():
            if any(keyword in code for keyword in keywords):
                return lang

        return "unknown"


def create_expert_executor(model=None, project_dir=None):
    """Factory for creating executor"""
    return ExpertExecutor(model, project_dir)


def execute_task(task: str, context: str = "", model=None) -> Dict:
    """Execute task"""
    executor = ExpertExecutor(model)
    return executor.execute_task(task, context)
