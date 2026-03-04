import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from brain.router import route_chat

WORKING_DIR = os.getcwd()


class TaskExecutor:
    """Agent that executes real tasks on the machine"""

    def __init__(self):
        self.working_dir = WORKING_DIR

    def run_command(self, command, timeout=30):
        """Run a shell command and return output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
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
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return {"success": True, "message": f"Created: {filepath}"}
        except Exception as e:
            return {"success": False, "message": f"Error creating file: {e}"}

    def read_file(self, filepath):
        """Read a file"""
        try:
            path = Path(filepath)
            if path.exists():
                return {"success": True, "content": path.read_text()}
            return {"success": False, "message": "File not found"}
        except Exception as e:
            return {"success": False, "message": f"Error reading file: {e}"}

    def list_files(self, directory="."):
        """List files in directory"""
        try:
            path = Path(directory)
            files = [str(f) for f in path.iterdir() if f.is_file()]
            return {"success": True, "files": files}
        except Exception as e:
            return {"success": False, "message": f"Error listing files: {e}"}


class PlanningAgent:
    """Agent that breaks down tasks into steps"""

    def plan(self, user_request):
        prompt = f"""You are a task planner. Break down this request into clear, executable steps.

Request: {user_request}

Respond with a numbered list of steps. Each step should be a single actionable task.
Example:
1. Create project directory structure
2. Write main HTML file
3. Add CSS styling
4. Test the application

Steps:"""

        result = route_chat([{"role": "user", "content": prompt}])
        return result


class ExecutionAgent:
    """Agent that executes code and files"""

    def __init__(self):
        self.executor = TaskExecutor()

    def execute_step(self, step):
        """Execute a single step"""
        step_lower = step.lower()

        if (
            "create file" in step_lower
            or "write file" in step_lower
            or "create" in step_lower
        ):
            return self._handle_create(step)
        elif "run" in step_lower or "execute" in step_lower or "install" in step_lower:
            return self._handle_run(step)
        elif "read" in step_lower or "check" in step_lower or "list" in step_lower:
            return self._handle_read(step)
        else:
            return self._handle_general(step)

    def _handle_create(self, step):
        prompt = f"""Analyze this step and extract what file to create and its content.

Step: {step}

Respond in this format:
FILE: <filepath>
CONTENT:
```
<file content here>
```

If no specific content is provided, create a basic implementation."""

        result = route_chat([{"role": "user", "content": prompt}])

        if "FILE:" in result and "CONTENT:" in result:
            try:
                lines = result.split("\n")
                filepath = None
                content_start = None

                for i, line in enumerate(lines):
                    if line.startswith("FILE:"):
                        filepath = line.replace("FILE:", "").strip()
                    if "CONTENT:" in line:
                        content_start = i
                        break

                if filepath and content_start:
                    content = "\n".join(lines[content_start + 1 :])
                    content = content.strip("`\n")
                    return self.executor.create_file(filepath, content)
            except:
                pass

        return {"success": False, "message": "Could not parse file creation"}

    def _handle_run(self, step):
        prompt = f"""Extract the exact terminal command to run from this step.

Step: {step}

Respond ONLY with the command, nothing else. Example: npm install"""

        command = route_chat([{"role": "user", "content": prompt}]).strip()

        if command:
            return self.executor.run_command(command)
        return {"success": False, "message": "No command found"}

    def _handle_read(self, step):
        prompt = f"""Extract the file path or directory to check from this step.

Step: {step}

Respond ONLY with the path."""

        path = route_chat([{"role": "user", "content": prompt}]).strip()

        if not path:
            return {"success": False, "message": "No path found"}

        if os.path.isfile(path):
            return self.executor.read_file(path)
        elif os.path.isdir(path):
            return self.executor.list_files(path)
        else:
            return self.executor.run_command(step)

    def _handle_general(self, step):
        """Use AI to decide what to do"""
        prompt = f"""Execute this task on the computer. 

Current directory: {self.executor.working_dir}

Task: {step}

What command should I run? Just give me the command."""

        command = route_chat([{"role": "user", "content": prompt}]).strip()

        if command and len(command) < 500:
            return self.executor.run_command(command)

        return {"success": False, "message": "Could not determine action"}


class ReviewAgent:
    """Agent that reviews and improves code"""

    def review(self, task, result):
        prompt = f"""Review this task completion:

Original Task: {task}

Result: {result}

Provide brief feedback. If there are issues, suggest fixes."""

        return route_chat([{"role": "user", "content": prompt}])


class AutonomousAgent:
    """Main orchestrator that coordinates all agents"""

    def __init__(self):
        self.planner = PlanningAgent()
        self.executor = ExecutionAgent()
        self.reviewer = ReviewAgent()

    def run(self, user_request, mode="auto"):
        """Execute user request autonomously"""

        steps = []

        if mode in ["auto", "plan"]:
            plan = self.planner.plan(user_request)
            steps = self._parse_steps(plan)

        if not steps:
            steps = [user_request]

        results = []

        for i, step in enumerate(steps, 1):
            print(f"\n[Step {i}/{len(steps)}] {step[:60]}...")

            result = self.executor.execute_step(step)
            results.append({"step": step, "result": result})

            if result.get("success"):
                print(f"  ✓ Done")
                if result.get("stdout"):
                    print(f"  Output: {result['stdout'][:200]}")
            else:
                print(f"  ✗ {result.get('message', 'Failed')}")

        if mode in ["auto", "review"]:
            print("\n[Review] Analyzing results...")
            review = self.reviewer.review(user_request, str(results))
            return review

        return f"Completed {len(results)} steps. {sum(1 for r in results if r['result'].get('success'))} successful."

    def _parse_steps(self, plan):
        """Parse numbered steps from plan"""
        steps = []
        lines = plan.split("\n")
        for line in lines:
            line = line.strip()
            if line and (
                line[0].isdigit() or line.startswith("-") or line.startswith("•")
            ):
                step = line.lstrip("0123456789.-•) ").strip()
                if step:
                    steps.append(step)
        return steps[:5]
