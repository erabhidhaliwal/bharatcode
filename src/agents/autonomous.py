import os
import json
import subprocess
from pathlib import Path

WORKING_DIR = os.getcwd()
MEMORY_FILE = os.path.join(WORKING_DIR, ".bharat_memory.json")


class ProjectMemory:
    """Memory system to remember projects and tasks"""

    def __init__(self):
        self.projects = {}
        self.load()

    def load(self):
        """Load memory from file"""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as f:
                    self.projects = json.load(f)
            except:
                self.projects = {}

    def save(self):
        """Save memory to file"""
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.projects, f, indent=2)

    def add_project(self, name, request, folder, files, status="created"):
        """Add a project to memory"""
        self.projects[name.lower()] = {
            "name": name,
            "request": request,
            "folder": folder,
            "files": files,
            "status": status,
        }
        self.save()

    def get_project(self, name):
        """Get a project by name"""
        name = name.lower()
        if name in self.projects:
            return self.projects[name]

        for key, proj in self.projects.items():
            if name in key or key in name:
                return proj
        return None

    def list_projects(self):
        """List all projects"""
        return list(self.projects.values())

    def update_project(self, name, updates):
        """Update a project"""
        name = name.lower()
        if name in self.projects:
            self.projects[name].update(updates)
            self.save()
            return True
        return False


class TaskExecutor:
    """Agent that executes real tasks on the machine"""

    def __init__(self, project_dir=None):
        self.project_dir = project_dir
        if project_dir:
            os.makedirs(project_dir, exist_ok=True)

    def get_working_dir(self):
        return self.project_dir or WORKING_DIR

    def run_command(self, command, timeout=60):
        """Run a shell command and return output"""
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
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:500],
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": -1,
            }
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}

    def create_file(self, filepath, content):
        """Create a file with content"""
        try:
            cwd = self.get_working_dir()
            if self.project_dir and not filepath.startswith("/"):
                filepath = os.path.join(self.project_dir, filepath)
            else:
                filepath = os.path.join(cwd, filepath)

            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return {"success": True, "message": f"✓ Created: {filepath}"}
        except Exception as e:
            return {"success": False, "message": f"✗ Error: {e}"}

    def read_file(self, filepath):
        """Read a file"""
        try:
            cwd = self.get_working_dir()
            if self.project_dir and not filepath.startswith("/"):
                filepath = os.path.join(self.project_dir, filepath)
            else:
                filepath = os.path.join(cwd, filepath)

            path = Path(filepath)
            if path.exists():
                return {"success": True, "content": path.read_text()}
            return {"success": False, "message": "File not found"}
        except Exception as e:
            return {"success": False, "message": f"Error: {e}"}

    def list_files(self, directory="."):
        """List files in directory"""
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
                    files.append(str(f.relative_to(path)))
            return {"success": True, "files": files}
        except Exception as e:
            return {"success": False, "message": f"Error: {e}"}


class ExecutionAgent:
    """Agent that executes code and files"""

    def __init__(self, project_dir=None, memory=None):
        self.executor = TaskExecutor(project_dir)
        self.memory = memory

    def execute_step(self, step, context=""):
        """Execute a single step"""

        prompt = f"""{context}

Analyze this task and decide what to do:

Task: {step}

You need to either:
1. CREATE A FILE - if it involves writing code, HTML, CSS, JS, Python, etc.
2. RUN A COMMAND - if it involves npm, git, python, etc.

Respond in this exact format:
ACTION: CREATE
FILENAME: index.html
CONTENT:
```html
<!DOCTYPE html>
<html>
<head><title>Example</title></head>
<body>Hello</body>
</html>
```

OR for commands:
ACTION: COMMAND
COMMAND: npm install

Keep content minimal but functional."""

        from brain.router import route_chat

        result = route_chat([{"role": "user", "content": prompt}])

        result = result.strip()

        if "ACTION: CREATE" in result.upper():
            return self._handle_create(result)
        elif "ACTION: COMMAND" in result.upper():
            return self._handle_command(result)
        else:
            return self.executor.run_command(step)

    def _handle_create(self, response):
        """Handle file creation"""
        lines = response.split("\n")
        filename = None
        content_lines = []
        in_content = False

        for line in lines:
            if line.startswith("FILENAME:"):
                filename = line.replace("FILENAME:", "").strip()
            elif "CONTENT:" in line.upper():
                in_content = True
                continue
            elif in_content and line.strip() in ["```", "```"]:
                continue
            elif in_content:
                content_lines.append(line)

        if not filename:
            return {"success": False, "message": "No filename found"}

        content = "\n".join(content_lines).strip()

        if content:
            return self.executor.create_file(filename, content)
        else:
            return {"success": False, "message": "No content found"}

    def _handle_command(self, response):
        """Handle command execution"""
        lines = response.split("\n")
        command = None

        for line in lines:
            if line.startswith("COMMAND:"):
                command = line.replace("COMMAND:", "").strip()
                break

        if command:
            return self.executor.run_command(command, timeout=120)

        return {"success": False, "message": "No command found"}


class AutonomousAgent:
    """Main orchestrator with memory"""

    def __init__(self, project_name=None, memory=None):
        self.project_name = project_name
        self.project_dir = None
        self.memory = memory or ProjectMemory()

        if project_name:
            self.project_dir = os.path.join(WORKING_DIR, project_name)

    def run(self, user_request, mode="auto"):
        """Execute user request with memory"""

        if not self.project_dir:
            safe_name = self._extract_name(user_request)
            self.project_dir = os.path.join(WORKING_DIR, safe_name)

        os.makedirs(self.project_dir, exist_ok=True)
        print(f"\n📁 Project folder: {self.project_dir}")

        existing_project = self.memory.get_project(self.project_name or safe_name)

        context = ""
        if existing_project:
            context = f"""CONTEXT - This is an existing project:
- Original request: {existing_project.get("request", "")}
- Folder: {existing_project.get("folder", "")}
- Files: {existing_project.get("files", [])}

Improve/extend the existing project based on the new request."""

        steps = [
            f"Create SPEC.md - Detailed specification for: {user_request}",
            f"Create index.html - Main HTML file",
            f"Create styles.css - Beautiful styling",
            f"Create script.js - JavaScript functionality",
            f"Verify and list all created files",
        ]

        executor = ExecutionAgent(self.project_dir, self.memory)
        results = []

        for i, step in enumerate(steps, 1):
            print(f"\n[Step {i}/{len(steps)}] {step[:50]}...")

            result = executor.execute_step(step, context=context)
            results.append({"step": step, "result": result})

            if result.get("success"):
                print(f"  ✓ Done")
                if result.get("message"):
                    print(f"     {result['message'][:80]}")
            else:
                print(f"  ⚠ {result.get('message', 'Note')[:60]}")

        files = executor.executor.list_files(".")
        file_list = files.get("files", []) if files.get("success") else []

        if file_list:
            print(f"\n📂 Files created ({len(file_list)}):")
            for f in file_list[:10]:
                print(f"  • {f}")

        project_name = self.project_name or safe_name
        self.memory.add_project(
            name=project_name,
            request=user_request,
            folder=self.project_dir,
            files=file_list,
            status="created",
        )

        summary = f"""✅ Project: {project_name}

Location: {self.project_dir}

Files: {len(file_list)}
"""
        for f in file_list[:10]:
            summary += f"• {f}\n"

        summary += f"""
To view:
  cd {self.project_dir}
  # Open index.html in browser

To improve later, just say:
  "improve {project_name}"
  "add more features to {project_name}"
"""

        return summary

    def improve(self, user_request):
        """Improve existing project"""

        if not self.project_name:
            return "No project selected. Create a project first."

        project = self.memory.get_project(self.project_name)
        if not project:
            return f"Project '{self.project_name}' not found in memory."

        self.project_dir = project["folder"]

        context = f"""CONTEXT - Improving existing project:
- Original request: {project.get("request", "")}
- Folder: {project.get("folder", "")}
- Existing files: {project.get("files", [])}

Make improvements based on: {user_request}"""

        steps = [
            f"Improve the website based on: {user_request}",
            f"Update existing files as needed",
            f"Add new features: {user_request}",
        ]

        executor = ExecutionAgent(self.project_dir, self.memory)

        for i, step in enumerate(steps, 1):
            print(f"\n[Improve {i}/{len(steps)}] {step[:50]}...")
            result = executor.execute_step(step, context=context)

            if result.get("success"):
                print(f"  ✓ Done")
            else:
                print(f"  ⚠ {result.get('message', 'Note')[:60]}")

        files = executor.executor.list_files(".")
        file_list = files.get("files", []) if files.get("success") else []

        self.memory.update_project(
            self.project_name, {"files": file_list, "last_update": user_request}
        )

        return f"""✅ Improved: {self.project_name}

Files: {len(file_list)}
Location: {self.project_dir}"""

    def _extract_name(self, request):
        """Extract project name from request"""
        words = request.lower().split()
        for word in ["called", "named", "name"]:
            if word in words:
                idx = words.index(word)
                if idx + 1 < len(words):
                    name = words[idx + 1].strip(".,!?")
                    if name and len(name) > 1:
                        return name
        return "project_" + "".join(c for c in request[:15] if c.isalnum()).lower()


def get_memory():
    """Get the shared memory instance"""
    return ProjectMemory()
