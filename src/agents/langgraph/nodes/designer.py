"""
LangGraph Designer Node
Converts DesignExpertAgent logic to LangGraph node
"""

import json
from typing import Dict, Any, Optional
from ..state import AgentState
from ..llm import chat_with_model_json, chat_with_model


DESIGNER_SYSTEM_PROMPT = """You are BharatCode Design Expert - an elite UI/UX design agent.

Design expertise:
- Typography (font pairing, hierarchy, readability)
- Color theory (palettes, psychology, contrast)
- Layout design (grid, asymmetry, white space)
- Animation & micro-interactions
- Accessibility standards (WCAG)
- Latest design trends
- Component design systems

Generate stunning, modern, on-trend designs."""


def designer_node(state: AgentState) -> AgentState:
    """
    Designer node - generates UI/UX design for the project.
    """
    user_request = state.get("user_request", "")
    project_name = state.get("project_name", "Project")
    iteration = state.get("iteration", 0)

    print(f"\n{'='*60}")
    print(f"DESIGNER NODE - Iteration {iteration + 1}")
    print(f"{'='*60}")
    print(f"Project: {project_name}")

    # Generate design components
    design_components = _generate_design_components(project_name, user_request)

    # Update state
    state["design_components"] = design_components
    state["design"] = {
        "project_name": project_name,
        "components": design_components,
        "palette": _get_default_palette(),
        "typography": _get_default_typography(),
    }
    state["current_phase"] = "executing"

    # Add message
    state["messages"] = state.get("messages", []) + [
        {"role": "assistant", "content": f"Design created for {project_name}"}
    ]

    print(f"✓ Design created")
    print(f"  Components: {len(design_components)}")

    return state


def _generate_design_components(project_name: str, requirements: str) -> Dict[str, Any]:
    """Generate design components using LLM"""

    # First, generate the design spec using LLM
    prompt = f"""{DESIGNER_SYSTEM_PROMPT}

Project: {project_name}
Requirements: {requirements}

Generate a complete website design specification. Include:
1. Color palette (primary, secondary, accent, background, text)
2. Typography (headings font, body font)
3. Layout structure (hero, features, pricing, etc.)
4. Component styles (buttons, cards, forms)

Return as JSON:
{{
  "colors": {{
    "primary": "#hexcode",
    "secondary": "#hexcode",
    "accent": "#hexcode",
    "background": "#hexcode",
    "text": "#hexcode"
  }},
  "typography": {{
    "heading_font": "Font Name",
    "body_font": "Font Name"
  }},
  "components": ["hero", "features", "pricing", "contact"],
  "style": "modern|minimalist|glassmorphism|dark"
}}"""

    response = chat_with_model_json(
        [{"role": "user", "content": prompt}],
        system_prompt=DESIGNER_SYSTEM_PROMPT,
    )

    if isinstance(response, dict):
        return response

    # Fallback to default design
    return _get_default_design()


def _get_default_palette() -> Dict[str, str]:
    """Get default color palette"""
    return {
        "primary": "#6366F1",
        "secondary": "#8B5CF6",
        "accent": "#EC4899",
        "background": "#0F172A",
        "surface": "#1E293B",
        "text": "#E2E8F0",
        "text_secondary": "#94A3B8",
    }


def _get_default_typography() -> Dict[str, str]:
    """Get default typography"""
    return {
        "heading_font": "Inter",
        "body_font": "Inter",
        "display_font": "Space Grotesk",
    }


def _get_default_design() -> Dict[str, Any]:
    """Get default design specification"""
    return {
        "colors": _get_default_palette(),
        "typography": _get_default_typography(),
        "components": ["hero", "features", "pricing", "footer"],
        "style": "modern",
    }


def generate_html(state: AgentState) -> AgentState:
    """
    Generate complete HTML from design components.
    """
    design = state.get("design", {})
    project_name = state.get("project_name", "Project")

    if not design:
        state["error"] = "No design to generate HTML from"
        return state

    # Generate HTML using LLM
    prompt = f"""Generate a complete HTML file for:

Project: {project_name}

Design:
{json.dumps(design, indent=2)}

Create a complete, production-ready HTML file with embedded CSS and JavaScript.
Make it modern, responsive, and visually stunning.
Include all the components mentioned in the design."""

    html_content = chat_with_model(
        [{"role": "user", "content": prompt}],
        system_prompt="You are an expert frontend developer.",
    )

    # Try to extract HTML from response
    html_file = _extract_html_from_response(html_content, project_name)

    if html_file:
        state["files_created"] = state.get("files_created", []) + [html_file]

    return state


def _extract_html_from_response(response: str, project_name: str) -> Optional[str]:
    """Extract and save HTML from LLM response"""
    import re

    # Look for code blocks
    html_match = re.search(r"```html\n(.*?)\n```", response, re.DOTALL)
    if html_match:
        html_content = html_match.group(1)
    else:
        # Try to find any HTML content
        html_match = re.search(r"<html.*</html>", response, re.DOTALL)
        if html_match:
            html_content = html_match.group(0)
        else:
            # Use the whole response as HTML
            html_content = response

    # Save to file
    filename = f"{project_name.lower().replace(' ', '_')}.html"

    try:
        with open(filename, "w") as f:
            f.write(html_content)
        return filename
    except Exception as e:
        print(f"Error saving HTML: {e}")
        return None


__all__ = ["designer_node", "generate_html"]
