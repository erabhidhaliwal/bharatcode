import os
import subprocess
import shutil
from pathlib import Path
from brain.router import route_chat

WORKING_DIR = os.getcwd()


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

    def __init__(self, project_dir=None):
        self.executor = TaskExecutor(project_dir)

    def execute_step(self, step):
        """Execute a single step - either create file or run command"""

        prompt = f"""Analyze this task and decide what to do:

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

Keep content minimal but functional. Use code blocks properly."""

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
    """Main orchestrator"""

    def __init__(self, project_name=None):
        self.project_name = project_name
        self.project_dir = None

        if project_name:
            self.project_dir = os.path.join(WORKING_DIR, project_name)

    def run(self, user_request, mode="auto"):
        """Execute user request"""

        if not self.project_dir:
            safe_name = "".join(c for c in user_request[:20] if c.isalnum()).lower()
            self.project_dir = os.path.join(WORKING_DIR, f"project_{safe_name}")

        os.makedirs(self.project_dir, exist_ok=True)
        print(f"\n📁 Project folder: {self.project_dir}")

        steps = [
            f"Create a detailed specification document SPEC.md for: {user_request}",
            f"Create index.html - main HTML file for: {user_request}",
            f"Create styles.css - beautiful styling for: {user_request}",
            f"Create script.js - JavaScript functionality for: {user_request}",
            f"Verify the website works - list all files created",
        ]

        executor = ExecutionAgent(self.project_dir)
        results = []

        for i, step in enumerate(steps, 1):
            print(f"\n[Step {i}/{len(steps)}] {step[:50]}...")

            result = executor.execute_step(step)
            results.append({"step": step, "result": result})

            if result.get("success"):
                print(f"  ✓ Done")
                if result.get("message"):
                    print(f"     {result['message'][:80]}")
            else:
                print(f"  ⚠ {result.get('message', 'Note')[:60]}")

        files = executor.executor.list_files(".")
        if files.get("success"):
            print(f"\n📂 Files created ({len(files.get('files', []))}):")
            for f in files.get("files", [])[:10]:
                print(f"  • {f}")

        summary = f"""✅ Project created: {self.project_name or "project"}

Location: {self.project_dir}

Files created:
"""
        if files.get("success"):
            for f in files.get("files", [])[:10]:
                summary += f"• {f}\n"

        summary += f"""
To view the website:
  cd {self.project_dir}
  # Open index.html in browser
"""

        return summary
