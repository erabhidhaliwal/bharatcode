"""
BharatCode Pro - UI/UX Design Expert Agent
Advanced design generation with trend learning and style mastery
Generates beautiful, trend-aware designs without watermarks
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class DesignTrend(Enum):
    """Current design trends"""
    MINIMALISM = "minimalism"
    MAXIMALISM = "maximalism"
    GLASSMORPHISM = "glassmorphism"
    NEUMORPHISM = "neumorphism"
    DARK_MODE = "dark_mode"
    BRUTALISM = "brutalism"
    ORGANIC = "organic"
    ART_DECO = "art_deco"
    RETRO_FUTURISTIC = "retro_futuristic"
    MICRO_INTERACTIONS = "micro_interactions"
    GRADIENT_HEAVY = "gradient_heavy"
    TYPOGRAPHY_FOCUSED = "typography_focused"
    SUSTAINABLE = "sustainable"
    INCLUSIVE = "inclusive"


class ColorPalette(Enum):
    """Modern color palettes"""
    VIBRANT = "vibrant"
    PASTEL = "pastel"
    EARTHY = "earthy"
    COOL_TONES = "cool_tones"
    MONOCHROMATIC = "monochromatic"
    ANALOGOUS = "analogous"
    COMPLEMENTARY = "complementary"
    NEON = "neon"


class ComponentType(Enum):
    """UI component types"""
    HERO = "hero"
    NAVBAR = "navbar"
    CARD = "card"
    BUTTON = "button"
    FORM = "form"
    MODAL = "modal"
    FOOTER = "footer"
    SIDEBAR = "sidebar"
    DROPDOWN = "dropdown"
    TABS = "tabs"
    BADGE = "badge"
    ALERT = "alert"
    PAGINATION = "pagination"
    TESTIMONIAL = "testimonial"
    PRICING = "pricing"
    FEATURES = "features"
    CTA = "cta"
    STATS = "stats"
    TIMELINE = "timeline"
    ACCORDION = "accordion"


DESIGN_SYSTEM_PROMPT = """You are BharatCode Design Expert - an elite UI/UX design agent.

DESIGN MASTERY:
- Typography expertise (font pairing, hierarchy, readability)
- Color theory (palettes, psychology, contrast)
- Layout design (grid, asymmetry, white space)
- Animation & micro-interactions
- Accessibility standards (WCAG, color contrast)
- Latest design trends and patterns
- Brand identity & consistency
- Component design systems

CURRENT DESIGN TRENDS:
{design_trends}

COLOR PSYCHOLOGY:
- Red: Energy, urgency, passion
- Blue: Trust, stability, calm
- Green: Growth, health, nature
- Purple: Luxury, creativity, mystery
- Orange: Enthusiasm, warmth, creativity
- Yellow: Optimism, clarity, attention
- Pink: Compassion, playfulness
- Black: Power, sophistication, mystery
- White: Cleanliness, simplicity, space

TYPOGRAPHY MASTERY:
Best Display: Playfair Display, Montserrat, Bebas Neue, Poppins, Raleway, Space Grotesk
Best Body: Inter, Roboto, Open Sans, Lato, Segoe UI, SF Pro
Font Pairing: Always pair a distinctive display with refined body font

DESIGN PRINCIPLES:
1. Visual Hierarchy - Guide viewer's eye
2. Contrast - Make important elements stand out
3. Alignment - Create order and structure
4. Repetition - Build consistency
5. Proximity - Group related elements
6. White Space - Breathe and emphasize
7. Color Harmony - Create emotional response
8. Accessibility - Inclusive design
9. Consistency - Unified experience
10. Innovation - Fresh approaches

CURRENT PROJECT: {project_context}
REQUIREMENTS: {design_requirements}
AESTHETIC DIRECTION: {aesthetic_direction}

Generate design that is:
✓ Stunning and memorable
✓ On-trend but timeless
✓ Accessible and inclusive
✓ Fully responsive
✓ Performant
✓ Without watermarks
✓ Production-ready"""


class DesignAsset:
    """Represents a design asset with metadata"""

    def __init__(self, name: str, asset_type: str, content: str):
        self.name = name
        self.asset_type = asset_type
        self.content = content
        self.created_at = datetime.now().isoformat()
        self.trends_used = []
        self.color_palette = None
        self.typography = None
        self.accessibility_score = 0


class DesignTrendLearner:
    """Learns and tracks design trends from internet sources"""

    def __init__(self):
        self.trends = {}
        self.trend_history = []
        self.learned_patterns = {}
        self.color_palettes = {}
        self.typography_patterns = {}
        self.load_trend_data()

    def load_trend_data(self):
        """Load design trend data"""
        self.trends = {
            "2025_2026": {
                "dominant": [
                    DesignTrend.GLASSMORPHISM,
                    DesignTrend.DARK_MODE,
                    DesignTrend.MICRO_INTERACTIONS,
                    DesignTrend.GRADIENT_HEAVY,
                ],
                "emerging": [
                    DesignTrend.ORGANIC,
                    DesignTrend.SUSTAINABLE,
                    DesignTrend.INCLUSIVE,
                    DesignTrend.TYPOGRAPHY_FOCUSED,
                ],
                "colors": {
                    "primary": ["#0F172A", "#1E293B", "#000000"],
                    "accent": ["#3B82F6", "#8B5CF6", "#EC4899", "#06B6D4"],
                    "gradients": [
                        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                        "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
                        "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
                        "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
                        "linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)",
                    ],
                },
                "typography": {
                    "display": ["Space Grotesk", "Montserrat", "Poppins", "Playfair Display"],
                    "body": ["Inter", "Roboto", "Open Sans", "DM Sans"],
                    "monospace": ["JetBrains Mono", "Space Mono", "IBM Plex Mono"],
                },
                "animations": {
                    "transitions": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                    "hover_effects": "subtle scale and shadow",
                    "scroll_animations": "reveal on scroll with IntersectionObserver",
                    "loading": "minimal skeleton screens",
                    "micro": "spring-based physics animations",
                },
                "spacing": {
                    "xs": "4px", "sm": "8px", "md": "16px",
                    "lg": "24px", "xl": "32px", "2xl": "48px", "3xl": "64px",
                },
                "border_radius": {
                    "sm": "6px", "md": "8px", "lg": "12px",
                    "xl": "16px", "2xl": "24px", "full": "9999px",
                },
            }
        }

        self.color_palettes = {
            ColorPalette.VIBRANT: {
                "primary": "#FF6B6B", "secondary": "#4ECDC4",
                "accent": "#FFE66D", "bg": "#FFFFFF",
                "surface": "#F8FAFC", "text": "#2D3436",
                "text_secondary": "#636E72",
            },
            ColorPalette.PASTEL: {
                "primary": "#FFB3D9", "secondary": "#B3E5FC",
                "accent": "#E1BEE7", "bg": "#FAFAFA",
                "surface": "#FFFFFF", "text": "#424242",
                "text_secondary": "#757575",
            },
            ColorPalette.EARTHY: {
                "primary": "#8B6F47", "secondary": "#D4A574",
                "accent": "#C9B896", "bg": "#F5F1E8",
                "surface": "#FDFBF7", "text": "#3E2723",
                "text_secondary": "#5D4037",
            },
            ColorPalette.COOL_TONES: {
                "primary": "#667EEA", "secondary": "#764BA2",
                "accent": "#06B6D4", "bg": "#0F172A",
                "surface": "#1E293B", "text": "#E2E8F0",
                "text_secondary": "#94A3B8",
            },
            ColorPalette.MONOCHROMATIC: {
                "primary": "#1A1A2E", "secondary": "#16213E",
                "accent": "#0F3460", "bg": "#FFFFFF",
                "surface": "#F1F5F9", "text": "#1E293B",
                "text_secondary": "#64748B",
            },
            ColorPalette.NEON: {
                "primary": "#00F5FF", "secondary": "#FF00E5",
                "accent": "#39FF14", "bg": "#0A0A0A",
                "surface": "#1A1A1A", "text": "#FFFFFF",
                "text_secondary": "#B0B0B0",
            },
            ColorPalette.COMPLEMENTARY: {
                "primary": "#6366F1", "secondary": "#F97316",
                "accent": "#10B981", "bg": "#FFFFFF",
                "surface": "#F8FAFC", "text": "#1E293B",
                "text_secondary": "#64748B",
            },
            ColorPalette.ANALOGOUS: {
                "primary": "#7C3AED", "secondary": "#2563EB",
                "accent": "#DB2777", "bg": "#FFFFFF",
                "surface": "#F5F3FF", "text": "#1E1B4B",
                "text_secondary": "#6B7280",
            },
        }

    def analyze_internet_trends(self) -> Dict:
        """Analyze current design trends using LLM"""
        try:
            from brain.router import route_chat
            prompt = """Analyze the current design trends on popular design platforms 
            (Dribbble, Behance, Pinterest, Design Systems). Focus on:
            1. Most used color schemes
            2. Popular typography combinations  
            3. Trending layout patterns
            4. Animation styles
            5. Component designs
            6. Accessibility approaches
            Return JSON with insights."""

            response = route_chat([
                {"role": "system", "content": "You are a design trend analyst expert in UX/UI."},
                {"role": "user", "content": prompt},
            ])

            self.trend_history.append({
                "timestamp": datetime.now().isoformat(),
                "analysis": response,
            })
            return self._parse_trend_analysis(response)
        except Exception:
            return self.trends.get("2025_2026", {})

    def learn_pattern(self, category: str, pattern_name: str, pattern_data: Dict):
        """Learn and store new design pattern"""
        if category not in self.learned_patterns:
            self.learned_patterns[category] = {}
        self.learned_patterns[category][pattern_name] = {
            "data": pattern_data,
            "learned_at": datetime.now().isoformat(),
            "usage_count": 0,
            "effectiveness_score": 0.0,
        }

    def get_palette(self, palette_type: ColorPalette = None) -> Dict:
        """Get color palette by type or default trending"""
        if palette_type and palette_type in self.color_palettes:
            return self.color_palettes[palette_type]
        return self.color_palettes[ColorPalette.COOL_TONES]

    def get_fonts(self) -> Dict:
        """Get current trending font combinations"""
        return self.trends["2025_2026"]["typography"]

    def get_animations(self) -> Dict:
        """Get current animation trends"""
        return self.trends["2025_2026"]["animations"]

    def get_spacing(self) -> Dict:
        """Get spacing scale"""
        return self.trends["2025_2026"]["spacing"]

    def get_radius(self) -> Dict:
        """Get border radius scale"""
        return self.trends["2025_2026"]["border_radius"]

    def _parse_trend_analysis(self, response: str) -> Dict:
        """Parse trend analysis response"""
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except Exception:
            pass
        return {"raw": response}


class UIComponentGenerator:
    """Generates UI components with modern design"""

    def __init__(self, trend_learner: DesignTrendLearner):
        self.trend_learner = trend_learner
        self.components = {}

    def _get_design_tokens(self, palette_type: ColorPalette = None):
        """Get all design tokens for generation"""
        return {
            "palette": self.trend_learner.get_palette(palette_type),
            "fonts": self.trend_learner.get_fonts(),
            "anims": self.trend_learner.get_animations(),
            "spacing": self.trend_learner.get_spacing(),
            "radius": self.trend_learner.get_radius(),
        }

    def generate_button(self, label: str, style: str = "primary",
                        size: str = "md", icon: Optional[str] = None,
                        palette_type: ColorPalette = None) -> Dict:
        """Generate a stylish button component"""
        t = self._get_design_tokens(palette_type)
        p, f, a = t["palette"], t["fonts"], t["anims"]

        colors = {"primary": p["primary"], "secondary": p["secondary"], "accent": p["accent"]}
        color = colors.get(style, p["primary"])
        size_map = {"sm": ("10px 20px", "13px"), "md": ("14px 28px", "15px"), "lg": ("18px 36px", "17px")}
        pad, fsize = size_map.get(size, size_map["md"])

        html = f"""<button class="btn btn-{style} btn-{size}">
  {f'<span class="btn-icon">{icon}</span>' if icon else ''}
  <span class="btn-label">{label}</span>
</button>"""

        css = f""".btn {{
  padding: {pad}; border: none; border-radius: {t['radius']['md']};
  font-weight: 600; cursor: pointer; font-size: {fsize};
  transition: {a['transitions']}; font-family: '{f['body'][0]}', sans-serif;
  display: inline-flex; align-items: center; gap: 8px;
  text-decoration: none; position: relative; overflow: hidden;
}}
.btn-{style} {{
  background: {color}; color: {p['bg'] if style != 'accent' else p['text']};
}}
.btn-{style}:hover {{
  transform: translateY(-2px);
  box-shadow: 0 8px 25px {color}40;
  filter: brightness(1.1);
}}
.btn-{style}:active {{ transform: translateY(0); }}
.btn-icon {{ font-size: 1.1em; }}"""

        self.components[f"button_{style}_{size}"] = {"html": html, "css": css}
        return {"html": html, "css": css}

    def generate_card(self, title: str, description: str,
                      image_placeholder: bool = True,
                      gradient_bg: bool = True,
                      palette_type: ColorPalette = None) -> Dict:
        """Generate a modern card component"""
        t = self._get_design_tokens(palette_type)
        p, f = t["palette"], t["fonts"]
        grad = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"

        html = f"""<div class="card">
  {f'<div class="card-image" style="background: {grad};"></div>' if image_placeholder else ''}
  <div class="card-content">
    <h3 class="card-title">{title}</h3>
    <p class="card-description">{description}</p>
  </div>
</div>"""

        css = f""".card {{
  background: {p.get('surface', p['bg'])}; border-radius: {t['radius']['lg']};
  overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  transition: {t['anims']['transitions']};
  border: 1px solid rgba(0,0,0,0.05);
}}
.card:hover {{
  transform: translateY(-6px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.12);
}}
.card-image {{ width: 100%; height: 200px; background-size: cover; background-position: center; }}
.card-content {{ padding: {t['spacing']['lg']}; }}
.card-title {{
  font-family: '{f['display'][0]}', sans-serif; font-size: 20px;
  font-weight: 700; color: {p['primary']}; margin-bottom: 8px;
}}
.card-description {{
  font-family: '{f['body'][0]}', sans-serif; font-size: 15px;
  color: {p.get('text_secondary', p['text'])}; line-height: 1.7;
}}"""

        self.components["card"] = {"html": html, "css": css}
        return {"html": html, "css": css}

    def generate_navigation(self, items: List[str], brand_name: str = "BharatDesign",
                            palette_type: ColorPalette = None) -> Dict:
        """Generate modern navigation component"""
        t = self._get_design_tokens(palette_type)
        p, f = t["palette"], t["fonts"]

        nav_items = "".join(
            [f'<li><a href="#{item.lower().replace(" ", "-")}">{item}</a></li>' for item in items]
        )

        html = f"""<nav class="navbar" role="navigation" aria-label="Main navigation">
  <div class="navbar-container">
    <a class="navbar-brand" href="/" aria-label="{brand_name} Home">{brand_name}</a>
    <button class="navbar-toggle" aria-label="Toggle menu" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>
    <ul class="navbar-menu" role="menubar">{nav_items}</ul>
  </div>
</nav>"""

        css = f""".navbar {{
  background: {p['bg']}; padding: 16px 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  position: sticky; top: 0; z-index: 1000;
  font-family: '{f['body'][0]}', sans-serif;
  backdrop-filter: blur(12px);
}}
.navbar-container {{
  max-width: 1200px; margin: 0 auto; padding: 0 24px;
  display: flex; justify-content: space-between; align-items: center;
}}
.navbar-brand {{
  font-size: 22px; font-weight: 800; text-decoration: none;
  font-family: '{f['display'][0]}', sans-serif;
  color: {p['primary']};
  background: linear-gradient(135deg, {p['primary']}, {p['secondary']});
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.navbar-menu {{
  display: flex; list-style: none; gap: 32px; margin: 0; padding: 0;
}}
.navbar-menu a {{
  color: {p['text']}; text-decoration: none; font-weight: 500;
  font-size: 15px; transition: color 0.3s; position: relative;
}}
.navbar-menu a:hover {{ color: {p['primary']}; }}
.navbar-menu a::after {{
  content: ''; position: absolute; bottom: -4px; left: 0;
  width: 0; height: 2px; background: {p['primary']};
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
.navbar-menu a:hover::after {{ width: 100%; }}
.navbar-toggle {{ display: none; background: none; border: none; cursor: pointer; padding: 4px; }}
.navbar-toggle span {{
  display: block; width: 24px; height: 2px;
  background: {p['text']}; margin: 5px 0;
  transition: {t['anims']['transitions']};
}}
@media (max-width: 768px) {{
  .navbar-toggle {{ display: block; }}
  .navbar-menu {{
    display: none; flex-direction: column; position: absolute;
    top: 100%; left: 0; right: 0; background: {p['bg']};
    padding: 16px 24px; gap: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  }}
  .navbar-menu.active {{ display: flex; }}
}}"""

        self.components["navigation"] = {"html": html, "css": css}
        return {"html": html, "css": css}

    def generate_hero_section(self, title: str, subtitle: str,
                              cta_text: str = "Get Started",
                              trend: DesignTrend = DesignTrend.GLASSMORPHISM,
                              palette_type: ColorPalette = None) -> Dict:
        """Generate modern hero section"""
        t = self._get_design_tokens(palette_type)
        p, f = t["palette"], t["fonts"]

        html = f"""<section class="hero" aria-label="Hero">
  <div class="hero-bg" aria-hidden="true">
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
    <div class="blob blob-3"></div>
  </div>
  <div class="hero-content">
    <h1 class="hero-title">{title}</h1>
    <p class="hero-subtitle">{subtitle}</p>
    <div class="hero-actions">
      <button class="hero-cta">{cta_text}</button>
      <button class="hero-cta-secondary">Learn More</button>
    </div>
  </div>
</section>"""

        css = f""".hero {{
  position: relative; min-height: 100vh;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden; background: {p['bg']};
}}
.hero-bg {{ position: absolute; width: 100%; height: 100%; top: 0; left: 0; }}
.blob {{
  position: absolute; border-radius: 50%;
  filter: blur(80px); opacity: 0.25;
}}
.blob-1 {{
  width: 400px; height: 400px; background: {p['primary']};
  top: 10%; left: 10%; animation: blobFloat 8s ease-in-out infinite;
}}
.blob-2 {{
  width: 350px; height: 350px; background: {p['secondary']};
  bottom: 15%; right: 15%; animation: blobFloat 10s ease-in-out infinite reverse;
}}
.blob-3 {{
  width: 250px; height: 250px; background: {p['accent']};
  top: 50%; left: 50%; animation: blobFloat 12s ease-in-out infinite 2s;
}}
@keyframes blobFloat {{
  0%, 100% {{ transform: translate(0, 0) scale(1); }}
  33% {{ transform: translate(30px, -30px) scale(1.05); }}
  66% {{ transform: translate(-20px, 20px) scale(0.95); }}
}}
.hero-content {{
  position: relative; z-index: 10; text-align: center;
  max-width: 800px; padding: 0 24px;
}}
.hero-title {{
  font-family: '{f['display'][0]}', sans-serif;
  font-size: clamp(36px, 6vw, 72px); font-weight: 800;
  margin: 0 0 24px; line-height: 1.1;
  background: linear-gradient(135deg, {p['primary']}, {p['secondary']});
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.hero-subtitle {{
  font-family: '{f['body'][0]}', sans-serif;
  font-size: clamp(16px, 2vw, 20px); color: {p.get('text_secondary', p['text'])};
  margin-bottom: 40px; line-height: 1.7; max-width: 600px; margin-left: auto; margin-right: auto;
}}
.hero-actions {{ display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }}
.hero-cta {{
  padding: 16px 40px; font-size: 16px; border: none; border-radius: {t['radius']['lg']};
  background: linear-gradient(135deg, {p['primary']}, {p['secondary']});
  color: white; cursor: pointer; font-weight: 700;
  transition: {t['anims']['transitions']};
  font-family: '{f['body'][0]}', sans-serif;
}}
.hero-cta:hover {{
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 16px 40px {p['primary']}40;
}}
.hero-cta-secondary {{
  padding: 16px 40px; font-size: 16px;
  border: 2px solid {p['primary']}40; border-radius: {t['radius']['lg']};
  background: transparent; color: {p['text']};
  cursor: pointer; font-weight: 600;
  transition: {t['anims']['transitions']};
  font-family: '{f['body'][0]}', sans-serif;
}}
.hero-cta-secondary:hover {{
  border-color: {p['primary']}; background: {p['primary']}10;
}}"""

        self.components["hero"] = {"html": html, "css": css}
        return {"html": html, "css": css}

    def generate_footer(self, brand_name: str = "BharatDesign",
                        sections: Dict = None, palette_type: ColorPalette = None) -> Dict:
        """Generate modern footer"""
        t = self._get_design_tokens(palette_type)
        p, f = t["palette"], t["fonts"]

        if not sections:
            sections = {
                "Product": ["Features", "Pricing", "Docs", "Changelog"],
                "Company": ["About", "Blog", "Careers", "Contact"],
                "Legal": ["Privacy", "Terms", "License"],
            }

        cols = ""
        for sec_title, links in sections.items():
            link_items = "".join([f'<li><a href="#{l.lower()}">{l}</a></li>' for l in links])
            cols += f'<div class="footer-col"><h4>{sec_title}</h4><ul>{link_items}</ul></div>'

        html = f"""<footer class="footer" role="contentinfo">
  <div class="footer-container">
    <div class="footer-brand">
      <h3>{brand_name}</h3>
      <p>Creating beautiful digital experiences.</p>
    </div>
    <div class="footer-links">{cols}</div>
  </div>
  <div class="footer-bottom">
    <p>&copy; {datetime.now().year} {brand_name}. All rights reserved.</p>
  </div>
</footer>"""

        css = f""".footer {{
  background: {p.get('surface', p['bg'])}; padding: 64px 0 0;
  font-family: '{f['body'][0]}', sans-serif;
  border-top: 1px solid rgba(0,0,0,0.06);
}}
.footer-container {{
  max-width: 1200px; margin: 0 auto; padding: 0 24px;
  display: flex; gap: 64px; flex-wrap: wrap;
}}
.footer-brand {{ flex: 1; min-width: 250px; }}
.footer-brand h3 {{
  font-family: '{f['display'][0]}', sans-serif;
  font-size: 22px; font-weight: 800; color: {p['primary']}; margin-bottom: 12px;
}}
.footer-brand p {{ color: {p.get('text_secondary', p['text'])}; line-height: 1.7; }}
.footer-links {{ display: flex; gap: 48px; flex-wrap: wrap; flex: 2; }}
.footer-col h4 {{
  font-weight: 700; color: {p['text']}; margin-bottom: 16px; font-size: 15px;
}}
.footer-col ul {{ list-style: none; padding: 0; margin: 0; }}
.footer-col li {{ margin-bottom: 10px; }}
.footer-col a {{
  color: {p.get('text_secondary', p['text'])}; text-decoration: none;
  font-size: 14px; transition: color 0.2s;
}}
.footer-col a:hover {{ color: {p['primary']}; }}
.footer-bottom {{
  max-width: 1200px; margin: 48px auto 0; padding: 24px;
  border-top: 1px solid rgba(0,0,0,0.06); text-align: center;
}}
.footer-bottom p {{ color: {p.get('text_secondary', p['text'])}; font-size: 13px; }}"""

        self.components["footer"] = {"html": html, "css": css}
        return {"html": html, "css": css}

    def generate_features_section(self, features: List[Dict] = None,
                                   palette_type: ColorPalette = None) -> Dict:
        """Generate features grid section"""
        t = self._get_design_tokens(palette_type)
        p, f = t["palette"], t["fonts"]

        if not features:
            features = [
                {"icon": "⚡", "title": "Lightning Fast", "desc": "Optimized for speed and performance"},
                {"icon": "🎨", "title": "Beautiful Design", "desc": "Stunning, modern visual aesthetics"},
                {"icon": "🔒", "title": "Secure", "desc": "Enterprise-grade security built-in"},
                {"icon": "📱", "title": "Responsive", "desc": "Perfect on every device and screen"},
                {"icon": "♿", "title": "Accessible", "desc": "WCAG 2.1 AA compliant out of the box"},
                {"icon": "🚀", "title": "Scalable", "desc": "Grows with your needs seamlessly"},
            ]

        cards = ""
        for feat in features:
            cards += f"""<div class="feature-card">
  <div class="feature-icon">{feat['icon']}</div>
  <h3 class="feature-title">{feat['title']}</h3>
  <p class="feature-desc">{feat['desc']}</p>
</div>"""

        html = f"""<section class="features-section" aria-label="Features">
  <div class="features-container">
    <h2 class="section-title">Why Choose Us</h2>
    <p class="section-subtitle">Everything you need to build amazing products</p>
    <div class="features-grid">{cards}</div>
  </div>
</section>"""

        css = f""".features-section {{
  padding: 96px 0; background: {p['bg']};
  font-family: '{f['body'][0]}', sans-serif;
}}
.features-container {{ max-width: 1200px; margin: 0 auto; padding: 0 24px; }}
.section-title {{
  text-align: center; font-family: '{f['display'][0]}', sans-serif;
  font-size: clamp(28px, 4vw, 42px); font-weight: 800; color: {p['text']};
  margin-bottom: 12px;
}}
.section-subtitle {{
  text-align: center; color: {p.get('text_secondary', p['text'])};
  font-size: 18px; margin-bottom: 56px; max-width: 500px; margin-left: auto; margin-right: auto;
}}
.features-grid {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 32px;
}}
.feature-card {{
  padding: 32px; border-radius: {t['radius']['xl']};
  background: {p.get('surface', p['bg'])};
  border: 1px solid rgba(0,0,0,0.05);
  transition: {t['anims']['transitions']};
}}
.feature-card:hover {{
  transform: translateY(-4px);
  box-shadow: 0 16px 40px rgba(0,0,0,0.08);
  border-color: {p['primary']}30;
}}
.feature-icon {{ font-size: 36px; margin-bottom: 16px; }}
.feature-title {{
  font-family: '{f['display'][0]}', sans-serif;
  font-size: 18px; font-weight: 700; color: {p['text']}; margin-bottom: 8px;
}}
.feature-desc {{
  color: {p.get('text_secondary', p['text'])}; font-size: 15px; line-height: 1.7;
}}"""

        self.components["features"] = {"html": html, "css": css}
        return {"html": html, "css": css}

    def generate_pricing_section(self, plans: List[Dict] = None,
                                  palette_type: ColorPalette = None) -> Dict:
        """Generate pricing cards section"""
        t = self._get_design_tokens(palette_type)
        p, f = t["palette"], t["fonts"]

        if not plans:
            plans = [
                {"name": "Starter", "price": "Free", "features": ["5 Projects", "Basic Support", "1GB Storage"], "cta": "Get Started", "popular": False},
                {"name": "Pro", "price": "$29/mo", "features": ["Unlimited Projects", "Priority Support", "100GB Storage", "Custom Domain"], "cta": "Start Free Trial", "popular": True},
                {"name": "Enterprise", "price": "Custom", "features": ["Everything in Pro", "Dedicated Support", "Unlimited Storage", "SLA", "SSO"], "cta": "Contact Sales", "popular": False},
            ]

        cards = ""
        for plan in plans:
            pop = " pricing-popular" if plan.get("popular") else ""
            feats = "".join([f"<li>✓ {feat}</li>" for feat in plan["features"]])
            badge = f'<span class="pricing-badge">Most Popular</span>' if plan.get("popular") else ""
            cards += f"""<div class="pricing-card{pop}">
  {badge}
  <h3 class="pricing-name">{plan['name']}</h3>
  <div class="pricing-price">{plan['price']}</div>
  <ul class="pricing-features">{feats}</ul>
  <button class="pricing-cta">{plan['cta']}</button>
</div>"""

        html = f"""<section class="pricing-section" aria-label="Pricing">
  <div class="pricing-container">
    <h2 class="section-title">Simple Pricing</h2>
    <p class="section-subtitle">Choose the plan that works for you</p>
    <div class="pricing-grid">{cards}</div>
  </div>
</section>"""

        css = f""".pricing-section {{
  padding: 96px 0; background: {p.get('surface', p['bg'])};
  font-family: '{f['body'][0]}', sans-serif;
}}
.pricing-container {{ max-width: 1100px; margin: 0 auto; padding: 0 24px; }}
.pricing-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; align-items: start; }}
.pricing-card {{
  padding: 36px; border-radius: {t['radius']['xl']};
  background: {p['bg']}; border: 1px solid rgba(0,0,0,0.08);
  position: relative; transition: {t['anims']['transitions']};
}}
.pricing-card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.1); }}
.pricing-popular {{
  border-color: {p['primary']}; box-shadow: 0 8px 32px {p['primary']}20;
  transform: scale(1.03);
}}
.pricing-popular:hover {{ transform: scale(1.03) translateY(-4px); }}
.pricing-badge {{
  position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
  background: linear-gradient(135deg, {p['primary']}, {p['secondary']});
  color: white; padding: 4px 20px; border-radius: {t['radius']['full']};
  font-size: 13px; font-weight: 700;
}}
.pricing-name {{ font-family: '{f['display'][0]}', sans-serif; font-size: 20px; font-weight: 700; color: {p['text']}; margin-bottom: 8px; }}
.pricing-price {{ font-size: 36px; font-weight: 800; color: {p['primary']}; margin-bottom: 24px; }}
.pricing-features {{ list-style: none; padding: 0; margin: 0 0 32px; }}
.pricing-features li {{ padding: 8px 0; color: {p.get('text_secondary', p['text'])}; font-size: 15px; }}
.pricing-cta {{
  width: 100%; padding: 14px; border: none; border-radius: {t['radius']['md']};
  font-weight: 700; font-size: 15px; cursor: pointer; transition: {t['anims']['transitions']};
  font-family: '{f['body'][0]}', sans-serif;
}}
.pricing-popular .pricing-cta {{
  background: linear-gradient(135deg, {p['primary']}, {p['secondary']});
  color: white;
}}
.pricing-popular .pricing-cta:hover {{ box-shadow: 0 8px 24px {p['primary']}40; }}
.pricing-card:not(.pricing-popular) .pricing-cta {{
  background: {p.get('surface', p['bg'])}; color: {p['text']};
  border: 1px solid rgba(0,0,0,0.12);
}}
.pricing-card:not(.pricing-popular) .pricing-cta:hover {{ border-color: {p['primary']}; color: {p['primary']}; }}"""

        self.components["pricing"] = {"html": html, "css": css}
        return {"html": html, "css": css}

    def generate_form(self, fields: List[Dict] = None,
                      palette_type: ColorPalette = None) -> Dict:
        """Generate a modern form component"""
        t = self._get_design_tokens(palette_type)
        p, f = t["palette"], t["fonts"]

        if not fields:
            fields = [
                {"name": "name", "type": "text", "label": "Full Name", "placeholder": "John Doe"},
                {"name": "email", "type": "email", "label": "Email Address", "placeholder": "john@example.com"},
                {"name": "message", "type": "textarea", "label": "Message", "placeholder": "Your message..."},
            ]

        inputs = ""
        for field in fields:
            fid = f"form-{field['name']}"
            if field["type"] == "textarea":
                inputs += f"""<div class="form-group">
  <label for="{fid}">{field['label']}</label>
  <textarea id="{fid}" name="{field['name']}" placeholder="{field.get('placeholder', '')}" rows="4"></textarea>
</div>"""
            else:
                inputs += f"""<div class="form-group">
  <label for="{fid}">{field['label']}</label>
  <input type="{field['type']}" id="{fid}" name="{field['name']}" placeholder="{field.get('placeholder', '')}">
</div>"""

        html = f"""<form class="modern-form" aria-label="Contact form">
  {inputs}
  <button type="submit" class="form-submit">Send Message</button>
</form>"""

        css = f""".modern-form {{
  max-width: 560px; margin: 0 auto; padding: 40px;
  background: {p.get('surface', p['bg'])}; border-radius: {t['radius']['xl']};
  border: 1px solid rgba(0,0,0,0.05);
  font-family: '{f['body'][0]}', sans-serif;
}}
.form-group {{ margin-bottom: 20px; }}
.form-group label {{
  display: block; margin-bottom: 6px; font-weight: 600;
  font-size: 14px; color: {p['text']};
}}
.form-group input, .form-group textarea {{
  width: 100%; padding: 12px 16px; border: 1.5px solid rgba(0,0,0,0.1);
  border-radius: {t['radius']['md']}; font-size: 15px;
  font-family: '{f['body'][0]}', sans-serif;
  background: {p['bg']}; color: {p['text']};
  transition: {t['anims']['transitions']};
  box-sizing: border-box;
}}
.form-group input:focus, .form-group textarea:focus {{
  outline: none; border-color: {p['primary']};
  box-shadow: 0 0 0 3px {p['primary']}20;
}}
.form-submit {{
  width: 100%; padding: 14px; border: none;
  border-radius: {t['radius']['md']};
  background: linear-gradient(135deg, {p['primary']}, {p['secondary']});
  color: white; font-weight: 700; font-size: 16px;
  cursor: pointer; transition: {t['anims']['transitions']};
  font-family: '{f['body'][0]}', sans-serif;
}}
.form-submit:hover {{
  transform: translateY(-2px);
  box-shadow: 0 8px 24px {p['primary']}40;
}}"""

        self.components["form"] = {"html": html, "css": css}
        return {"html": html, "css": css}

    def generate_all_components(self, brand_name: str = "BharatDesign",
                                 palette_type: ColorPalette = None) -> Dict:
        """Generate all standard components at once"""
        return {
            "navigation": self.generate_navigation(
                ["Home", "Features", "Pricing", "About", "Contact"],
                brand_name=brand_name, palette_type=palette_type,
            ),
            "hero": self.generate_hero_section(
                f"Welcome to {brand_name}",
                "Creating beautiful digital experiences that inspire and delight.",
                palette_type=palette_type,
            ),
            "features": self.generate_features_section(palette_type=palette_type),
            "pricing": self.generate_pricing_section(palette_type=palette_type),
            "card": self.generate_card("Feature Card", "Amazing features and more", palette_type=palette_type),
            "button": self.generate_button("Get Started", "primary", palette_type=palette_type),
            "form": self.generate_form(palette_type=palette_type),
            "footer": self.generate_footer(brand_name=brand_name, palette_type=palette_type),
        }


class DesignExpertAgent:
    """Master UI/UX Design Expert Agent"""

    def __init__(self):
        self.trend_learner = DesignTrendLearner()
        self.component_generator = UIComponentGenerator(self.trend_learner)
        self.designs = {}
        self.design_library = []
        self.learning_log = []

    def design_website(self, project_name: str, requirements: str = "",
                       target_audience: str = "",
                       brand_colors: Optional[List[str]] = None,
                       aesthetic: Optional[DesignTrend] = None,
                       palette_type: Optional[ColorPalette] = None) -> Dict:
        """Design complete website with all components"""
        # Generate all components
        components = self.component_generator.generate_all_components(
            brand_name=project_name, palette_type=palette_type,
        )

        # LLM design analysis
        design_analysis = ""
        try:
            from brain.router import route_chat
            trends = self.trend_learner.analyze_internet_trends()
            prompt = DESIGN_SYSTEM_PROMPT.format(
                design_trends=json.dumps(trends, indent=2)[:500],
                project_context=f"Project: {project_name}",
                design_requirements=requirements,
                aesthetic_direction=aesthetic.value if aesthetic else "modern",
            )
            design_analysis = route_chat([
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Design for: {requirements}. Audience: {target_audience}"},
            ])
        except Exception as e:
            design_analysis = f"Design generated with trending defaults. ({e})"

        design = {
            "project_name": project_name,
            "design_analysis": design_analysis,
            "components": components,
            "trends_used": [aesthetic.value if aesthetic else "modern"],
            "palette": self.trend_learner.get_palette(palette_type),
            "typography": self.trend_learner.get_fonts(),
            "created_at": datetime.now().isoformat(),
        }

        self.designs[project_name] = design
        self.learning_log.append({
            "event": "design_created", "project": project_name,
            "timestamp": datetime.now().isoformat(),
        })
        return design

    def generate_complete_html(self, project_name: str, components: Dict,
                               title: str = "Beautiful Design",
                               palette_type: ColorPalette = None) -> str:
        """Generate complete HTML with CSS from components"""
        p = self.trend_learner.get_palette(palette_type)
        f = self.trend_learner.get_fonts()

        all_css = "\n".join([comp.get("css", "") for comp in components.values() if isinstance(comp, dict)])
        all_html = "\n".join([comp.get("html", "") for comp in components.values() if isinstance(comp, dict)])

        google_fonts = "+".join([font.replace(" ", "+") for font in f["display"][:2] + f["body"][:2]])

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{title} - Built with BharatCode Design Expert">
  <title>{title}</title>
  <link href="https://fonts.googleapis.com/css2?family={google_fonts}&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      font-family: '{f['body'][0]}', -apple-system, BlinkMacSystemFont, sans-serif;
      background: {p['bg']}; color: {p['text']}; line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }}
    img {{ max-width: 100%; display: block; }}
    a {{ color: inherit; }}
    {all_css}
    @media (max-width: 768px) {{
      .hero-title {{ font-size: 32px !important; }}
      .features-grid {{ grid-template-columns: 1fr !important; }}
      .pricing-grid {{ grid-template-columns: 1fr !important; }}
    }}
  </style>
</head>
<body>
  {all_html}
  <script>
    // Mobile nav toggle
    const toggle = document.querySelector('.navbar-toggle');
    const menu = document.querySelector('.navbar-menu');
    if (toggle && menu) {{
      toggle.addEventListener('click', () => {{
        menu.classList.toggle('active');
        toggle.setAttribute('aria-expanded', menu.classList.contains('active'));
      }});
    }}
    // Scroll reveal
    const observer = new IntersectionObserver((entries) => {{
      entries.forEach(entry => {{
        if (entry.isIntersecting) {{
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }}
      }});
    }}, {{ threshold: 0.1 }});
    document.querySelectorAll('.feature-card, .pricing-card').forEach(el => {{
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = 'opacity 0.6s, transform 0.6s';
      observer.observe(el);
    }});
  </script>
</body>
</html>"""

    def design_ui_component(self, component_type: str, specifications: Dict,
                            design_system: Optional[str] = None) -> Dict:
        """Design individual UI component via LLM"""
        try:
            from brain.router import route_chat
            prompt = f"""Design a {component_type} component with specifications:
            {json.dumps(specifications, indent=2)}
            Design System: {design_system or 'Modern, trendy'}
            Provide: HTML structure, CSS styling, animations, accessibility, responsive."""
            response = route_chat([
                {"role": "system", "content": "You are expert in UI component design."},
                {"role": "user", "content": prompt},
            ])
            return {"component_type": component_type, "design": response, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            return {"component_type": component_type, "error": str(e)}

    def create_design_system(self, name: str, brand_colors: List[str],
                             typography: Dict, components: List[str]) -> Dict:
        """Create comprehensive design system"""
        design_system = {
            "name": name, "colors": brand_colors, "typography": typography,
            "components": components, "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
        }
        self.design_library.append(design_system)
        return {"status": "created", "design_system": design_system}

    def adapt_to_brand(self, brand_colors: List[str], brand_name: str,
                       tone: str = "professional") -> Dict:
        """Adapt designs to brand specifications"""
        return {
            "brand_name": brand_name, "colors": brand_colors, "tone": tone,
            "recommendations": {
                "typography": "Use elegant fonts matching brand tone",
                "components": "All components styled with brand colors",
                "animations": "Subtle animations matching brand personality",
                "imagery": "High-quality, consistent imagery style",
            },
            "adapted_at": datetime.now().isoformat(),
        }

    def export_design(self, project_name: str, format: str = "html") -> Dict:
        """Export design in various formats"""
        if project_name not in self.designs:
            return {"error": "Project not found"}

        project = self.designs[project_name]
        components = project.get("components", {})

        if format == "html":
            content = self.generate_complete_html(project_name, components, project_name)
            return {"format": "html", "content": content, "file": f"{project_name}.html"}
        elif format == "css":
            css = "\n".join([c.get("css", "") for c in components.values() if isinstance(c, dict)])
            return {"format": "css", "content": css, "file": f"{project_name}.css"}
        elif format == "json":
            return {"format": "json", "content": json.dumps(project, indent=2), "file": f"{project_name}.json"}
        return {"error": "Unsupported format"}

    def get_design_insights(self) -> Dict:
        """Get insights from design learning"""
        return {
            "designs_created": len(self.designs),
            "design_systems": len(self.design_library),
            "learning_events": len(self.learning_log),
            "trends_discovered": len(self.trend_learner.trend_history),
            "patterns_learned": len(self.trend_learner.learned_patterns),
            "available_palettes": [p.value for p in ColorPalette],
            "available_trends": [t.value for t in DesignTrend],
            "available_components": [c.value for c in ComponentType],
            "timestamp": datetime.now().isoformat(),
        }


def create_design_expert():
    """Factory for creating design expert agent"""
    return DesignExpertAgent()
