"""
Design Agent Orchestrator
Coordinates UI/UX design with backend and execution agents
Manages complete design-to-implementation workflow
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .design_expert_agent import DesignExpertAgent, DesignTrend, ColorPalette
from .design_asset_manager import DesignAssetManager


class DesignOrchestrator:
    """Orchestrates design with other agents and systems"""

    def __init__(self):
        self.design_expert = DesignExpertAgent()
        self.asset_manager = DesignAssetManager()
        self.design_projects = {}
        self.workflow_status = {}
        self.coordination_history = []

    def create_complete_design(self, project_name: str, requirements: str,
                               target_audience: str = "",
                               brand_colors: Optional[List[str]] = None,
                               backend_requirements: str = "",
                               aesthetic: Optional[str] = None,
                               palette: Optional[str] = None) -> Dict:
        """Create complete design with all assets and specifications"""

        # Map string to enums
        trend_enum = None
        if aesthetic:
            try:
                trend_enum = DesignTrend[aesthetic.upper()]
            except KeyError:
                pass

        palette_enum = None
        if palette:
            try:
                palette_enum = ColorPalette[palette.upper()]
            except KeyError:
                pass

        # 1. Generate Core Design
        design_result = self.design_expert.design_website(
            project_name=project_name,
            requirements=requirements,
            target_audience=target_audience,
            brand_colors=brand_colors,
            aesthetic=trend_enum,
            palette_type=palette_enum,
        )

        # 2. Generate Assets
        assets = self.asset_manager.get_complete_asset_package()

        # 3. Create Design System
        design_system = self.design_expert.create_design_system(
            name=f"{project_name} Design System",
            brand_colors=design_result.get("palette", {}),
            typography=design_result.get("typography", {}),
            components=list(design_result.get("components", {}).keys()),
        )

        # 4. Generate Code Packages
        html_code = self.design_expert.export_design(project_name, "html")
        css_code = self.design_expert.export_design(project_name, "css")

        # 5. Create Coordination Document
        coordination_doc = self._create_coordination_document(
            design=design_result,
            assets=assets,
            design_system=design_system,
            backend_specs=backend_requirements,
        )

        # 6. Package everything
        complete_package = {
            "project_name": project_name,
            "design": design_result,
            "assets": assets,
            "design_system": design_system,
            "coordination": coordination_doc,
            "exports": {
                "html": html_code,
                "css": css_code,
            },
            "status": "ready_for_implementation",
            "created_at": datetime.now().isoformat(),
        }

        self.design_projects[project_name] = complete_package

        return complete_package

    def _create_coordination_document(self, design: Dict, assets: Dict,
                                      design_system: Dict, backend_specs: str) -> Dict:
        """Create coordination document between design and engineering"""
        return {
            "integration_points": ["API", "Data Binding", "State Management"],
            "backend_requirements": backend_specs,
            "design_specifications": "Provided in design_system",
            "assets_manifest": f"{assets.get('total_assets', 0)} assets available",
            "responsive_strategy": "Mobile-first approach with breakpoints at 768px and 1200px",
            "accessibility_checklist": "WCAG 2.1 AA compliance required",
            "performance_guidelines": "Images optimized, lazy loading for off-screen elements",
            "created_at": datetime.now().isoformat(),
        }

    def adapt_design_to_brand(self, project_name: str, brand_colors: List[str],
                              brand_name: str, tone: str = "professional") -> Dict:
        """Adapt existing design to brand specifications"""
        return self.design_expert.adapt_to_brand(brand_colors, brand_name, tone)

    def create_design_component_spec(self, component_name: str,
                                     component_type: str, specifications: Dict) -> Dict:
        """Create detailed specification for single component"""
        return self.design_expert.design_ui_component(component_type, specifications)

    def generate_design_documentation(self, project_name: str) -> Dict:
        """Generate comprehensive design documentation"""
        if project_name not in self.design_projects:
            return {"error": f"Project '{project_name}' not found."}

        project = self.design_projects[project_name]
        return {
            "title": f"{project_name} Design Documentation",
            "design_system": project.get("design_system"),
            "components_overview": list(project.get("design", {}).get("components", {}).keys()),
            "assets_summary": self.asset_manager.get_design_assets_summary(),
            "generated_at": datetime.now().isoformat(),
        }

    def export_design_package(self, project_name: str, format: str = "complete") -> Dict:
        """Export complete design package"""
        if project_name not in self.design_projects:
            return {"error": f"Project '{project_name}' not found."}
            
        project = self.design_projects[project_name]
        
        if format == "complete":
            return project
            
        if format in project.get("exports", {}):
            return project["exports"][format]
            
        return {"error": f"Format '{format}' not supported."}

    def apply_design_trends(self, project_name: str) -> Dict:
        """Apply latest design trends to project"""
        trends = self.design_expert.trend_learner.analyze_internet_trends()
        return {
            "status": "trends_applied",
            "trends": trends,
            "timestamp": datetime.now().isoformat(),
        }

    def integrate_with_backend(self, project_name: str, backend_specs: Dict) -> Dict:
        """Integrate design with backend requirements"""
        return {
            "status": "integrated",
            "project": project_name,
            "backend_specs": backend_specs,
            "timestamp": datetime.now().isoformat(),
        }

    def get_design_insights(self) -> Dict:
        """Get insights about all designs"""
        return self.design_expert.get_design_insights()


class DesignToCodeGenerator:
    """Generates code from design specifications"""

    def __init__(self):
        self.generated_code = {}

    def generate_component_code(self, component_spec: Dict, language: str = "html") -> Dict:
        """Generate component code from specification"""
        if language == "html":
            return self._generate_html(component_spec)
        elif language == "react":
            return self._generate_react(component_spec)
        elif language == "vue":
            return self._generate_vue(component_spec)
        return {"error": f"Language '{language}' not supported"}

    def _generate_html(self, spec: Dict) -> Dict:
        return {"type": "html", "code": spec.get("html", ""), "css": spec.get("css", "")}

    def _generate_react(self, spec: Dict) -> Dict:
        html = spec.get("html", "")
        # Very basic conversion for illustrative purposes
        jsx = html.replace("class=", "className=").replace("<!--", "{/*").replace("-->", "*/}")
        react_code = f"""import React from 'react';
import './styles.css';

export const Component = () => {{
  return (
    <>
      {jsx}
    </>
  );
}};
"""
        return {"type": "react", "code": react_code, "css": spec.get("css", "")}

    def _generate_vue(self, spec: Dict) -> Dict:
        vue_code = f"""<template>
  {spec.get("html", "")}
</template>

<script setup>
// Component logic goes here
</script>

<style scoped>
{spec.get("css", "")}
</style>
"""
        return {"type": "vue", "code": vue_code}


def create_design_orchestrator():
    """Factory for creating design orchestrator"""
    return DesignOrchestrator()


def create_design_to_code_generator():
    """Factory for creating code generator"""
    return DesignToCodeGenerator()
