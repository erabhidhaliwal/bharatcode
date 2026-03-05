"""
Expert Agent Orchestrator
Coordinates planner, executor, and reviewer with auto-learning and evolution
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from .autonomous_expert import ExpertAutonomousAgent, ProjectMemory, ExpertiseLevel
from .planner_expert import ExpertPlanner, AdaptivePlanner
from .reviewer_expert import ExpertReviewer, ContinuousImprover
from .executor_expert import ExpertExecutor
from .design_expert_agent import DesignExpertAgent


class ExpertAgentOrchestrator:
    """Orchestrates expert agents for comprehensive project execution"""

    def __init__(self, project_name: Optional[str] = None):
        self.project_name = project_name
        self.memory = ProjectMemory()

        # Initialize expert agents
        self.autonomous_agent = ExpertAutonomousAgent(project_name)
        self.planner = AdaptivePlanner()
        self.reviewer = ExpertReviewer()
        self.improver = ContinuousImprover()
        self.design_expert = DesignExpertAgent()

        # Execution tracking
        self.execution_log = []
        self.metrics_log = []

    def execute_expert_workflow(self, user_request: str) -> Dict:
        """Execute comprehensive expert workflow"""
        print("\n" + "=" * 80)
        print("🚀 BHARAT CODE PRO - EXPERT EXECUTION WORKFLOW")
        print("=" * 80)

        # Phase 1: Planning
        print("\n📋 PHASE 1: EXPERT PLANNING & ARCHITECTURE")
        print("-" * 80)
        plan = self.planner.plan_with_learning(user_request)
        print(f"✓ Plan created with {len(plan.get('phases', []))} phases")

        # Phase 2: Dependency & Risk Analysis
        print("\n🔍 PHASE 2: DEPENDENCY & RISK ANALYSIS")
        print("-" * 80)
        dependencies = self.planner.planner.analyze_dependencies(plan)
        risks = self.planner.planner.identify_risks(plan)
        print(f"✓ Identified {len(risks)} risks")
        print(f"✓ Critical path: {dependencies.get('critical_path', [])[:3]}")

        # Phase 3: Architecture Planning
        print("\n🏗️  PHASE 3: ARCHITECTURE DESIGN")
        print("-" * 80)
        architecture = self.planner.planner.plan_architecture(user_request)
        testing_strategy = self.planner.planner.plan_testing_strategy(plan)
        print(f"✓ Architecture designed")
        print(f"✓ Testing strategy created")

        # Phase 4: UI/UX Design
        print("\n🎨 PHASE 4: UI/UX DESIGN EXPERT")
        print("-" * 80)
        design_result = self.design_expert.design_website(
            self.project_name or "MyProject", user_request
        )
        print(f"✓ UI/UX design created")

        # Phase 5: Execution
        print("\n⚙️  PHASE 5: EXPERT EXECUTION")
        print("-" * 80)
        execution_result = self.autonomous_agent.run(user_request)
        print(execution_result)

        # Phase 6: Code Review
        print("\n🔬 PHASE 6: EXPERT CODE REVIEW")
        print("-" * 80)
        review = self._conduct_comprehensive_review()
        print(
            f"✓ Code review complete - Quality: {review.get('overall_quality_score', 'N/A')}/100"
        )

        # Phase 7: Continuous Improvement
        print("\n✨ PHASE 7: CONTINUOUS IMPROVEMENT")
        print("-" * 80)
        improvements = self._perform_continuous_improvement()
        print(f"✓ Applied {len(improvements.get('improvements', []))} improvements")

        # Phase 8: Learning & Evolution
        print("\n🧠 PHASE 8: AUTO-LEARNING & EVOLUTION")
        print("-" * 80)
        self._record_learning(plan, {"result": execution_result}, review)
        self.memory.evolve_expertise()
        print(f"✓ Expertise level: {self.memory.expertise_level.name}")

        # Generate comprehensive report
        report = self._generate_comprehensive_report(plan, review, improvements, risks)

        return report

    def _conduct_comprehensive_review(self) -> Dict:
        """Conduct comprehensive code review"""
        # Read generated code files
        project_files = self.autonomous_agent.executor.executor.list_files()

        reviews = []
        for file_info in project_files.get("files", [])[:5]:
            filepath = file_info["path"]
            if filepath.endswith((".py", ".js", ".ts", ".go", ".java")):
                file_result = self.autonomous_agent.executor.executor.read_file(
                    filepath
                )
                if file_result["success"]:
                    review = self.reviewer.review_code(file_result["content"], filepath)
                    reviews.append(review)

        # Aggregate reviews
        if reviews:
            avg_score = sum(r.get("overall_quality_score", 0) for r in reviews) / len(
                reviews
            )
            all_issues = []
            for review in reviews:
                all_issues.extend(review.get("critical_issues", []))

            return {
                "overall_quality_score": avg_score,
                "files_reviewed": len(reviews),
                "critical_issues": all_issues,
                "reviews": reviews,
            }

        return {"overall_quality_score": 0, "files_reviewed": 0}

    def _perform_continuous_improvement(self) -> Dict:
        """Perform continuous code improvement"""
        project_files = self.autonomous_agent.executor.executor.list_files()

        improvements_made = []
        for file_info in project_files.get("files", [])[:3]:
            filepath = file_info["path"]
            if filepath.endswith((".py", ".js", ".ts")):
                file_result = self.autonomous_agent.executor.executor.read_file(
                    filepath
                )
                if file_result["success"]:
                    improvement = self.improver.iterative_improvement(
                        file_result["content"], iterations=2
                    )
                    improvements_made.append(
                        {
                            "file": filepath,
                            "improvement": improvement,
                        }
                    )

        return {"improvements": improvements_made}

    def _record_learning(self, plan: Dict, execution_result: Dict, review: Dict):
        """Record learning from execution"""
        self.memory.log_learning(
            "workflow_execution",
            {
                "plan": plan,
                "execution_result": execution_result,
                "review": review,
                "timestamp": datetime.now().isoformat(),
            },
            success=True,
        )

        # Extract and store patterns
        if plan.get("phases"):
            self.memory.add_knowledge(
                "patterns",
                "execution_phases",
                {
                    "phase_structure": [p.get("phase_name") for p in plan["phases"]],
                    "effectiveness": review.get("overall_quality_score", 0),
                },
            )

    def _generate_comprehensive_report(
        self,
        plan: Dict,
        review: Dict,
        improvements: Dict,
        risks: List[Dict],
    ) -> Dict:
        """Generate comprehensive execution report"""
        # Get files created
        files_list = []
        project_path = ""
        try:
            project_files = self.autonomous_agent.executor.executor.list_files()
            files_list = [f["path"] for f in project_files.get("files", [])]
            project_path = self.autonomous_agent.project_dir or ""
        except Exception:
            pass

        return {
            "project_name": self.autonomous_agent.project_name,
            "execution_timestamp": datetime.now().isoformat(),
            "expertise_level": self.memory.expertise_level.name,
            "summary": f"Project '{self.autonomous_agent.project_name}' created successfully with {len(files_list)} files. Quality score: {review.get('overall_quality_score', 0):.1f}/100",
            "files_created": files_list,
            "project_path": project_path,
            "planning": {
                "phases": len(plan.get("phases", [])),
                "complexity_level": plan.get("complexity_level"),
                "estimated_effort": plan.get("estimated_effort"),
            },
            "execution": {
                "status": "completed",
                "project_location": self.autonomous_agent.project_dir,
            },
            "quality": {
                "overall_score": review.get("overall_quality_score", 0),
                "files_reviewed": review.get("files_reviewed", 0),
                "critical_issues": len(review.get("critical_issues", [])),
                "improvements_applied": len(improvements.get("improvements", [])),
            },
            "risks": {
                "total_identified": len(risks),
                "high_risk_count": len(
                    [r for r in risks if r.get("probability") == "high"]
                ),
                "mitigation_strategies": [r.get("mitigation") for r in risks],
            },
            "learning": {
                "experiences_logged": len(self.memory.learning_log),
                "knowledge_base_size": len(self.memory.knowledge_base),
                "evolution_available": self.memory.expertise_level.value
                < ExpertiseLevel.VISIONARY.value,
            },
            "recommendations": self._generate_recommendations(review, risks),
        }

    def _generate_recommendations(self, review: Dict, risks: List[Dict]) -> List[str]:
        """Generate recommendations for future improvements"""
        recommendations = []

        # From review
        if review.get("overall_quality_score", 0) < 80:
            recommendations.append(
                "Focus on code quality improvements in next iteration"
            )

        # From risks
        high_risks = [r for r in risks if r.get("impact") == "high"]
        if high_risks:
            recommendations.append(f"Address {len(high_risks)} high-impact risks")

        recommendations.append(
            "Document architecture decisions for team knowledge base"
        )
        recommendations.append("Set up automated testing and CI/CD pipeline")

        return recommendations

    def execute_with_feedback_loop(
        self, user_request: str, max_iterations: int = 3
    ) -> Dict:
        """Execute with feedback loop for continuous improvement"""
        print("\n🔄 EXECUTING WITH FEEDBACK LOOP")

        results = {
            "iterations": [],
            "final_quality_score": 0,
            "convergence": False,
        }

        previous_score = 0

        for iteration in range(max_iterations):
            print(f"\n--- Iteration {iteration + 1}/{max_iterations} ---")

            # Execute workflow
            report = self.execute_expert_workflow(user_request)
            quality_score = report["quality"]["overall_score"]

            results["iterations"].append(
                {
                    "iteration": iteration + 1,
                    "quality_score": quality_score,
                    "improvements": report["quality"]["improvements_applied"],
                }
            )

            results["final_quality_score"] = quality_score

            # Check convergence
            if iteration > 0:
                improvement = quality_score - previous_score
                if improvement < 5:  # Less than 5% improvement
                    results["convergence"] = True
                    print(f"✓ Convergence reached at iteration {iteration + 1}")
                    break

            previous_score = quality_score

        return results


class ProjectExecutionManager:
    """Manages multiple projects with orchestrator"""

    def __init__(self):
        self.orchestrators = {}
        self.project_registry = {}

    def create_project(self, project_name: str) -> ExpertAgentOrchestrator:
        """Create and manage new project"""
        orchestrator = ExpertAgentOrchestrator(project_name)
        self.orchestrators[project_name] = orchestrator
        self.project_registry[project_name] = {
            "created_at": datetime.now().isoformat(),
            "status": "initialized",
        }
        return orchestrator

    def execute_project(self, project_name: str, request: str) -> Dict:
        """Execute project with orchestrator"""
        if project_name not in self.orchestrators:
            self.create_project(project_name)

        orchestrator = self.orchestrators[project_name]
        result = orchestrator.execute_expert_workflow(request)

        self.project_registry[project_name]["status"] = "completed"
        self.project_registry[project_name]["completed_at"] = datetime.now().isoformat()

        return result

    def get_project_status(self, project_name: str) -> Dict:
        """Get project status"""
        return self.project_registry.get(project_name, {})

    def list_projects(self) -> List[Dict]:
        """List all projects"""
        return [
            {"name": name, **status} for name, status in self.project_registry.items()
        ]


def create_orchestrator(project_name: Optional[str] = None) -> ExpertAgentOrchestrator:
    """Factory for creating orchestrator"""
    return ExpertAgentOrchestrator(project_name)


def execute_expert_project(project_name: str, request: str) -> Dict:
    """Execute expert project"""
    manager = ProjectExecutionManager()
    return manager.execute_project(project_name, request)
