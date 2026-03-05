"""
BharatCode Pro - Expert Level Autonomous Engineering Agent
Advanced capabilities: Auto-learning, evolution, knowledge accumulation, expert reasoning
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import hashlib
from enum import Enum
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

WORKING_DIR = os.getcwd()
MEMORY_FILE = os.path.join(WORKING_DIR, ".bharat_memory.json")
KNOWLEDGE_BASE_FILE = os.path.join(WORKING_DIR, ".bharat_knowledge.json")
LEARNING_LOG_FILE = os.path.join(WORKING_DIR, ".bharat_learning.json")


class ExpertiseLevel(Enum):
    """Expertise progression levels"""

    JUNIOR = 1
    INTERMEDIATE = 2
    SENIOR = 3
    ARCHITECT = 4
    VISIONARY = 5


class ProjectMemory:
    """Enhanced memory system with learning capabilities"""

    def __init__(self):
        self.projects = {}
        self.knowledge_base = {}
        self.learning_log = []
        self.expertise_level = ExpertiseLevel.SENIOR
        self.performance_metrics = {}
        self.load()

    def load(self):
        """Load all memory and knowledge"""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as f:
                    self.projects = json.load(f)
            except:
                self.projects = {}

        if os.path.exists(KNOWLEDGE_BASE_FILE):
            try:
                with open(KNOWLEDGE_BASE_FILE, "r") as f:
                    self.knowledge_base = json.load(f)
            except:
                self.knowledge_base = {}

        if os.path.exists(LEARNING_LOG_FILE):
            try:
                with open(LEARNING_LOG_FILE, "r") as f:
                    self.learning_log = json.load(f)
            except:
                self.learning_log = []

    def save(self):
        """Save all memory and knowledge"""
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.projects, f, indent=2)
        with open(KNOWLEDGE_BASE_FILE, "w") as f:
            json.dump(self.knowledge_base, f, indent=2)
        with open(LEARNING_LOG_FILE, "w") as f:
            json.dump(self.learning_log, f, indent=2)

    def add_project(self, name, request, folder, files, status="created"):
        """Add project with detailed metadata"""
        self.projects[name.lower()] = {
            "name": name,
            "request": request,
            "folder": folder,
            "files": files,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "complexity_score": self._calculate_complexity(request),
            "technologies": self._extract_technologies(request),
            "patterns_applied": [],
            "lessons_learned": [],
        }
        self.save()

    def get_project(self, name):
        name = name.lower()
        if name in self.projects:
            return self.projects[name]
        for key, proj in self.projects.items():
            if name in key or key in name:
                return proj
        return None

    def add_knowledge(self, category: str, topic: str, content: Dict):
        """Add to knowledge base for auto-learning"""
        if category not in self.knowledge_base:
            self.knowledge_base[category] = {}

        self.knowledge_base[category][topic] = {
            "content": content,
            "added_at": datetime.now().isoformat(),
            "access_count": 0,
            "last_used": None,
            "effectiveness_score": 0.0,
        }
        self.save()

    def get_knowledge(self, category: str, topic: Optional[str] = None) -> Dict:
        """Retrieve knowledge with learning tracking"""
        if category not in self.knowledge_base:
            return {}

        if topic:
            if topic in self.knowledge_base[category]:
                entry = self.knowledge_base[category][topic]
                entry["access_count"] += 1
                entry["last_used"] = datetime.now().isoformat()
                self.save()
                return entry["content"]
            return {}

        return self.knowledge_base[category]

    def log_learning(self, event: str, details: Dict, success: bool = True):
        """Log learning experiences for evolution"""
        self.learning_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "event": event,
                "details": details,
                "success": success,
            }
        )
        self.save()

    def evolve_expertise(self):
        """Auto-evolve expertise based on learning"""
        success_count = sum(1 for log in self.learning_log if log["success"])
        total_count = len(self.learning_log)

        if total_count > 0:
            success_rate = success_count / total_count

            if success_rate > 0.9 and total_count > 20:
                if self.expertise_level.value < ExpertiseLevel.VISIONARY.value:
                    self.expertise_level = ExpertiseLevel(
                        min(
                            self.expertise_level.value + 1,
                            ExpertiseLevel.VISIONARY.value,
                        )
                    )

    def _calculate_complexity(self, request: str) -> float:
        """Calculate project complexity"""
        keywords = {
            "distributed": 2.0,
            "microservices": 2.0,
            "machine learning": 2.0,
            "real-time": 1.8,
            "scalable": 1.6,
            "secure": 1.6,
            "performance": 1.4,
            "simple": 0.5,
            "basic": 0.4,
        }

        score = 1.0
        for keyword, multiplier in keywords.items():
            if keyword.lower() in request.lower():
                score *= multiplier

        return min(score, 5.0)

    def _extract_technologies(self, request: str) -> List[str]:
        """Extract technologies mentioned"""
        techs = [
            "Python",
            "JavaScript",
            "TypeScript",
            "Java",
            "Go",
            "Rust",
            "C++",
            "React",
            "Vue",
            "Angular",
            "Node.js",
            "Django",
            "FastAPI",
            "Docker",
            "Kubernetes",
            "AWS",
            "GCP",
            "Azure",
            "PostgreSQL",
            "MongoDB",
            "Redis",
            "GraphQL",
            "ML",
            "AI",
            "TensorFlow",
            "PyTorch",
            "scikit-learn",
            "WebSocket",
            "gRPC",
            "REST",
            "SOAP",
        ]

        found = []
        for tech in techs:
            if tech.lower() in request.lower():
                found.append(tech)

        return found

    def list_projects(self):
        return list(self.projects.values())

    def update_project(self, name, updates):
        name = name.lower()
        if name in self.projects:
            self.projects[name].update(updates)
            self.save()
            return True
        return False


EXPERT_SYSTEM_PROMPT = """You are BharatCode Pro - an EXPERT LEVEL autonomous senior software architect.

EXPERTISE LEVEL: {expertise_level}

CORE PRINCIPLES:
✓ Think like a principal engineer / CTO
✓ Design for scale, performance, and resilience
✓ Protect working code with surgical precision
✓ Refactor intelligently with comprehensive testing
✓ Optimize for both current and future needs
✓ Consider security, scalability, maintainability
✓ Apply architectural patterns expertly

EXECUTION MODEL:
1. ANALYZE DEEPLY - Understand context, dependencies, patterns
2. DESIGN PRECISELY - Architecture, data flow, error handling
3. IMPLEMENT CLEANLY - Production-ready, well-structured
4. REFACTOR INTELLIGENTLY - DRY, SOLID principles
5. TEST THOROUGHLY - Unit, integration, edge cases
6. OPTIMIZE FULLY - Performance, memory, security
7. DOCUMENT CLEARLY - For future maintainers

BEFORE WRITING CODE:
□ Review ALL existing files and architecture
□ Identify duplication and refactoring opportunities
□ Consider performance implications
□ Review security implications
□ Plan for scalability and maintenance
□ Check for patterns and anti-patterns
□ Design error handling and edge cases

NEVER:
✗ Produce incomplete or fragile code
✗ Introduce technical debt without justification
✗ Break working features without comprehensive testing
✗ Execute dangerous commands without safeguards
✗ Ignore architectural considerations
✗ Skip error handling and validation

ADVANCED CAPABILITIES:
- Multi-file refactoring with dependency tracking
- Performance optimization and benchmarking
- Security hardening and vulnerability assessment
- Scalability architecture design
- Design pattern application
- Code generation from specifications
- Automated testing framework setup
- CI/CD pipeline configuration

KNOWLEDGE BASE:
{knowledge_context}

PREVIOUS LESSONS:
{lessons_learned}"""


ARCHITECT_ANALYSIS_PROMPT = """You are an expert software architect analyzing this request.

Provide analysis in this format:

ARCHITECTURE_ANALYSIS:
- System Design: [high-level design]
- Components: [major components needed]
- Data Flow: [how data moves]
- Technology Stack: [recommended technologies]
- Scalability: [scaling strategy]
- Security: [security considerations]
- Performance: [performance targets]

IMPLEMENTATION_STRATEGY:
1. [First major step]
2. [Second major step]
3. [Continue...]

POTENTIAL_RISKS:
- [Risk 1]: [mitigation]
- [Risk 2]: [mitigation]

Request: {request}"""


class AdvancedExecutor:
    """Enhanced executor with expert capabilities"""

    def __init__(self, project_dir=None, memory=None):
        self.project_dir = project_dir
        self.memory = memory or ProjectMemory()
        if project_dir:
            os.makedirs(project_dir, exist_ok=True)

    def get_working_dir(self):
        return self.project_dir or WORKING_DIR

    def run_command(
        self, command: str, timeout: int = 60, safe_mode: bool = True
    ) -> Dict:
        """Execute command with safety checks"""
        dangerous_patterns = [
            "rm -rf /",
            "dd if=/dev/zero",
            "fork()",
            ": () { : | :& };",  # Bash fork bomb
            "sudo",
            "su -",
        ]

        if safe_mode and any(pattern in command for pattern in dangerous_patterns):
            return {
                "success": False,
                "error": "Command blocked for safety",
                "suggestion": "Use safer alternatives or disable safe_mode explicitly",
            }

        try:
            cwd = self.get_working_dir()
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:5000],
                "stderr": result.stderr[:2000],
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out",
                "timeout_sec": timeout,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_file(self, filepath: str, content: str, backup: bool = True) -> Dict:
        """Create file with backup capability"""
        try:
            cwd = self.get_working_dir()
            if self.project_dir and not filepath.startswith("/"):
                filepath = os.path.join(self.project_dir, filepath)
            else:
                filepath = os.path.join(cwd, filepath)

            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)

            # Backup existing file
            if backup and path.exists():
                backup_path = (
                    f"{filepath}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                path.rename(backup_path)

            path.write_text(content)
            return {"success": True, "path": str(filepath), "size": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_file(self, filepath: str) -> Dict:
        """Read file with metadata"""
        try:
            cwd = self.get_working_dir()
            if self.project_dir and not filepath.startswith("/"):
                filepath = os.path.join(self.project_dir, filepath)
            else:
                filepath = os.path.join(cwd, filepath)

            path = Path(filepath)
            if path.exists():
                content = path.read_text()
                return {
                    "success": True,
                    "content": content,
                    "size": len(content),
                    "lines": content.count("\n") + 1,
                }
            return {"success": False, "error": "File not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_files(self, directory: str = ".") -> Dict:
        """List files with metadata"""
        try:
            cwd = self.get_working_dir()
            if self.project_dir and not directory.startswith("/"):
                directory = os.path.join(self.project_dir, directory)
            else:
                directory = os.path.join(cwd, directory)

            path = Path(directory)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)

            files = []
            for f in path.rglob("*"):
                if f.is_file():
                    files.append(
                        {
                            "path": str(f.relative_to(path)),
                            "size": f.stat().st_size,
                            "modified": f.stat().st_mtime,
                        }
                    )

            return {"success": True, "files": files, "count": len(files)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_codebase(self, directory: str = ".") -> Dict:
        """Analyze existing codebase"""
        try:
            cwd = self.get_working_dir()
            if self.project_dir and not directory.startswith("/"):
                directory = os.path.join(self.project_dir, directory)
            else:
                directory = os.path.join(cwd, directory)

            path = Path(directory)
            stats = {
                "total_files": 0,
                "total_lines": 0,
                "by_language": {},
                "largest_files": [],
            }

            files_by_size = []

            for f in path.rglob("*"):
                if f.is_file() and not any(part.startswith(".") for part in f.parts):
                    stats["total_files"] += 1
                    ext = f.suffix.lower() or "unknown"

                    try:
                        content = f.read_text()
                        lines = content.count("\n") + 1
                        stats["total_lines"] += lines
                        files_by_size.append((str(f.relative_to(path)), lines))

                        if ext not in stats["by_language"]:
                            stats["by_language"][ext] = {"files": 0, "lines": 0}
                        stats["by_language"][ext]["files"] += 1
                        stats["by_language"][ext]["lines"] += lines
                    except:
                        pass

            stats["largest_files"] = sorted(
                files_by_size, key=lambda x: x[1], reverse=True
            )[:5]
            return {"success": True, "analysis": stats}
        except Exception as e:
            return {"success": False, "error": str(e)}


class ExpertExecutionAgent:
    """Expert-level execution agent with advanced capabilities"""

    def __init__(self, project_dir=None, memory=None):
        self.executor = AdvancedExecutor(project_dir, memory)
        self.memory = memory or ProjectMemory()

    def perform_architectural_analysis(self, request: str) -> Dict:
        """Perform deep architectural analysis"""
        from brain.router import route_chat

        prompt = ARCHITECT_ANALYSIS_PROMPT.format(request=request)
        result = route_chat([{"role": "user", "content": prompt}])

        return {
            "analysis": result,
            "timestamp": datetime.now().isoformat(),
        }

    def refactor_intelligently(self, filepath: str, context: str = "") -> Dict:
        """Intelligently refactor existing code"""
        file_result = self.executor.read_file(filepath)
        if not file_result["success"]:
            return file_result

        from brain.router import route_chat

        prompt = f"""You are an expert code refactorer.

Current code in {filepath}:
```
{file_result["content"]}
```

Context: {context}

Refactoring goals:
1. Improve readability and maintainability
2. Apply SOLID principles
3. Remove duplication
4. Optimize performance
5. Add type hints / documentation
6. Handle edge cases

Provide refactored code with explanation of changes."""

        result = route_chat([{"role": "user", "content": prompt}])
        self.memory.log_learning("refactor", {"file": filepath, "result": result})

        return {"success": True, "refactoring": result}

    def execute_expert_step(self, step: str, context: str = "") -> Dict:
        """Execute step with expert-level reasoning"""
        from brain.router import route_chat
        import re

        expertise = self.memory.expertise_level.name

        prompt = EXPERT_SYSTEM_PROMPT.format(
            expertise_level=expertise,
            knowledge_context=json.dumps(self.memory.knowledge_base, indent=2)[:1000],
            lessons_learned=json.dumps(self.memory.learning_log[-5:], indent=2)
            if self.memory.learning_log
            else "None yet",
        )

        full_prompt = f"""{prompt}

{context}

Task: {step}

IMPORTANT: You MUST use this exact format for each file:
FILENAME: <filename>
```<language>
[complete code here]
```

Example:
FILENAME: index.html
```html
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>Hello</body>
</html>
```

If running a command:
COMMAND: <command>"""

        result = route_chat(
            [
                {
                    "role": "system",
                    "content": "You are an expert code generator. Always start your response with FILENAME: <filename> followed by the code in a code block.",
                },
                {"role": "user", "content": full_prompt},
            ]
        )

        # Parse and execute CREATE actions
        files_created = 0
        commands_run = []

        # Extract FILENAME blocks - look for FILENAME: prefix
        filename_pattern = r"FILENAME:\s*(.+)"
        code_block_pattern = r"```\w*\n(.*)```"
        command_pattern = r"COMMAND:\s*(.+)"

        filenames = re.findall(filename_pattern, result, re.IGNORECASE)
        code_blocks = re.findall(code_block_pattern, result, re.DOTALL)
        commands = re.findall(command_pattern, result, re.IGNORECASE)

        # If no explicit filenames, try to infer from step context
        if not filenames and code_blocks:
            step_lower = step.lower()
            if (
                "index.html" in step_lower
                and "style" in step_lower
                and "script" in step_lower
            ):
                filenames = ["index.html", "styles.css", "script.js"]
            elif "index.html" in step_lower or "html" in step_lower:
                filenames = ["index.html"]
            elif "style" in step_lower or "css" in step_lower:
                filenames = ["styles.css"]
            elif "script" in step_lower or "javascript" in step_lower:
                filenames = ["script.js"]
            elif "spec" in step_lower:
                filenames = ["SPEC.md"]
            else:
                filenames = ["generated_file.txt"]

        # Ensure we have enough filenames for code blocks
        while len(filenames) < len(code_blocks):
            filenames.append(f"file_{len(filenames) + 1}.txt")

        # Create files
        for i, filename in enumerate(filenames):
            filename = filename.strip()
            code = code_blocks[i].strip() if i < len(code_blocks) else ""
            if code:
                create_result = self.executor.create_file(filename, code)
                if create_result.get("success"):
                    files_created += 1
                    print(f"    📄 Created: {filename}")

        # Run commands
        for cmd in commands:
            cmd = cmd.strip()
            if cmd:
                run_result = self.executor.run_command(cmd)
                if run_result.get("success"):
                    commands_run.append(cmd)
                    print(f"    ▶️  Ran: {cmd[:50]}")

        self.memory.log_learning(
            "execution_step",
            {"step": step, "files_created": files_created, "commands": commands_run},
            success=True,
        )

        return {
            "success": True,
            "result": result,
            "files_created": files_created,
            "commands": commands_run,
        }


class ExpertAutonomousAgent:
    """Expert-level autonomous agent with self-evolution"""

    def __init__(self, project_name: Optional[str] = None):
        self.project_name = project_name
        self.project_dir = None
        self.memory = ProjectMemory()
        self.executor = ExpertExecutionAgent(self.project_dir, self.memory)

    def run(self, user_request: str) -> str:
        """Execute expert-level project"""
        # Architectural analysis phase
        print("\n🧠 ARCHITECTURAL ANALYSIS")
        arch_analysis = self.executor.perform_architectural_analysis(user_request)
        print(f"Analysis complete")

        # Project setup
        if not self.project_name:
            self.project_name = self._extract_project_name(user_request)
        self.project_dir = os.path.join(WORKING_DIR, self.project_name)
        self.executor.executor.project_dir = self.project_dir

        print(f"\n📁 Project: {self.project_name}")
        print(f"Expertise Level: {self.memory.expertise_level.name}")

        # Codebase analysis if project exists
        existing_analysis = self.executor.executor.analyze_codebase()
        if existing_analysis["success"]:
            print(
                f"📊 Existing codebase: {existing_analysis['analysis']['total_files']} files"
            )

        # Execute expert steps
        print("\n⚡ EXPERT EXECUTION")
        steps = [
            f"Create index.html, styles.css, and script.js for: {user_request}",
            f"Verify all files are complete and functional",
        ]

        for i, step in enumerate(steps, 1):
            print(f"\n[{i}/{len(steps)}] {step}")
            result = self.executor.execute_expert_step(step, context=user_request)
            if result.get("files_created", 0) > 0:
                print(f"  ✓ Created {result['files_created']} file(s)")
            elif result.get("commands"):
                print(f"  ✓ Ran {len(result['commands'])} command(s)")
            else:
                print("  ✓ Complete")

        # Save project
        files = self.executor.executor.list_files()
        self.memory.add_project(
            name=self.project_name,
            request=user_request,
            folder=self.project_dir,
            files=[f["path"] for f in files.get("files", [])],
            status="created",
        )

        # Auto-evolve
        self.memory.evolve_expertise()

        return f"""
✅ EXPERT PROJECT COMPLETE: {self.project_name}

📊 Results:
  Location: {self.project_dir}
  Files: {files.get("count", 0)}
  Expertise Level: {self.memory.expertise_level.name}
  Knowledge Base: {len(self.memory.knowledge_base)} categories

🧠 Auto-Learning:
  Experiences logged: {len(self.memory.learning_log)}
  Success rate: {sum(1 for log in self.memory.learning_log if log["success"]) / max(len(self.memory.learning_log), 1) * 100:.1f}%
"""

    def _extract_project_name(self, request: str) -> str:
        """Extract project name from request"""
        words = request.lower().split()

        # Handle "name it <name>" pattern
        for i, word in enumerate(words):
            if word == "it" and i + 1 < len(words):
                name = words[i + 1].strip(".,!?")
                if name and len(name) > 1:
                    return name

        # Handle "called <name>", "named <name>", etc.
        for word in ["called", "named", "name"]:
            if word in words:
                idx = words.index(word)
                if idx + 1 < len(words):
                    name = words[idx + 1].strip(".,!?")
                    if name and len(name) > 1:
                        return name

        # Default: use first meaningful word
        for word in ["create", "build", "make"]:
            if word in words:
                idx = words.index(word)
                if idx + 1 < len(words):
                    name = words[idx + 1].strip(".,!?")
                    if name and len(name) > 1:
                        return name

        return "project_" + "".join(c for c in request[:15] if c.isalnum()).lower()


def get_memory():
    """Get or create memory instance"""
    return ProjectMemory()


def create_expert_agent(project_name=None):
    """Factory for creating expert agents"""
    return ExpertAutonomousAgent(project_name)
