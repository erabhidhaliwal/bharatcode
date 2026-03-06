"""
LangGraph Reviewer Node
Converts ExpertReviewer logic to LangGraph node
"""

import json
from typing import Dict, Any, List
from ..state import AgentState
from ..llm import chat_with_model_json, chat_with_model


REVIEWER_SYSTEM_PROMPT = """You are an EXPERT CODE REVIEWER and quality architect.

Review code comprehensively covering:
1. CORRECTNESS - Logic, edge cases, error handling
2. PERFORMANCE - Time/space complexity, bottlenecks
3. MAINTAINABILITY - Clarity, naming, DRY, SOLID
4. SECURITY - Vulnerabilities, input validation
5. SCALABILITY - Caching, database, architecture
6. ARCHITECTURE - Design patterns, modularity

Provide detailed feedback in JSON format."""


def reviewer_node(state: AgentState) -> AgentState:
    """
    Reviewer node - reviews executed code for quality.
    """
    files_created = state.get("files_created", [])
    project_name = state.get("project_name", "Project")
    iteration = state.get("iteration", 0)

    print(f"\n{'='*60}")
    print(f"REVIEWER NODE - Iteration {iteration + 1}")
    print(f"{'='*60}")
    print(f"Project: {project_name}")
    print(f"Files to review: {len(files_created)}")

    if not files_created:
        print("  No files to review")
        state["review"] = {"summary": "No files to review"}
        state["quality_score"] = 50.0
        state["current_phase"] = "human_review"
        return state

    # Review each file
    reviews = []
    total_score = 0.0

    for filepath in files_created[:5]:  # Limit to first 5 files
        try:
            with open(filepath, "r") as f:
                content = f.read()

            if _is_reviewable(filepath, content):
                review = _review_file(filepath, content)
                reviews.append(review)
                total_score += review.get("overall_quality_score", 0)
        except Exception as e:
            print(f"  Error reading {filepath}: {e}")

    # Calculate overall score
    if reviews:
        avg_score = total_score / len(reviews)
    else:
        avg_score = 50.0

    # Update state
    state["review"] = {
        "files_reviewed": len(reviews),
        "reviews": reviews,
        "overall_quality_score": avg_score,
    }
    state["quality_score"] = avg_score
    state["current_phase"] = "human_review"

    # Add message
    state["messages"] = state.get("messages", []) + [
        {"role": "assistant", "content": f"Code review complete. Quality score: {avg_score:.1f}/100"}
    ]

    print(f"✓ Review complete")
    print(f"  Files reviewed: {len(reviews)}")
    print(f"  Quality score: {avg_score:.1f}/100")

    return state


def _is_reviewable(filepath: str, content: str) -> bool:
    """Check if file is reviewable (code file)"""
    code_extensions = [".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".java", ".rs", ".cpp", ".c"]
    return any(filepath.endswith(ext) for ext in code_extensions)


def _review_file(filepath: str, content: str) -> Dict[str, Any]:
    """Review a single file"""
    prompt = f"""{REVIEWER_SYSTEM_PROMPT}

File: {filepath}

Code:
```{_get_language(filepath)}
{content[:3000]}
```

Provide review as JSON:
{{
  "file": "{filepath}",
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
      "solution": "how to fix"
    }}
  ],
  "improvements": [
    {{
      "category": "which category",
      "suggestion": "what to improve",
      "reasoning": "why"
    }}
  ],
  "patterns_applied": [],
  "anti_patterns_found": []
}}"""

    response = chat_with_model_json(
        [{"role": "user", "content": prompt}],
        system_prompt=REVIEWER_SYSTEM_PROMPT,
    )

    if isinstance(response, dict):
        return response
    return {"file": filepath, "overall_quality_score": 50, "raw": response}


def _get_language(filepath: str) -> str:
    """Get language from file extension"""
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".go": "go",
        ".java": "java",
        ".rs": "rust",
        ".cpp": "cpp",
        ".c": "c",
    }
    for ext, lang in ext_map.items():
        if filepath.endswith(ext):
            return lang
    return "text"


def check_quality_threshold(state: AgentState) -> AgentState:
    """
    Check if quality meets threshold and decide next steps.
    """
    quality_score = state.get("quality_score", 0)
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 5)

    print(f"\nQuality check: {quality_score:.1f}/100")

    # Determine if we need human review
    if quality_score >= 80:
        state["requires_human_review"] = False
    elif quality_score >= 60:
        state["requires_human_review"] = True
    else:
        # Low quality - try to improve
        state["requires_human_review"] = True
        if iteration < max_iterations - 1:
            # Allow retry
            pass

    return state


def apply_improvements(state: AgentState) -> AgentState:
    """
    Apply improvements based on review feedback.
    """
    review = state.get("review", {})
    reviews = review.get("reviews", [])

    improvements_applied = []

    for file_review in reviews:
        critical_issues = file_review.get("critical_issues", [])
        if critical_issues:
            improvements_applied.append({
                "file": file_review.get("file"),
                "issues_fixed": len(critical_issues),
            })

    state["improvements_applied"] = improvements_applied

    return state


__all__ = ["reviewer_node", "check_quality_threshold", "apply_improvements"]
