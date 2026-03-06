"""
LangGraph Memory Module
SqliteSaver for checkpointer and long-term memory
"""

import os
import json
from typing import Optional, Dict, Any, List


# Try to import LangGraph components
LANGGRAPH_AVAILABLE = False

try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    # Fallback for when LangGraph is not available
    SqliteSaver = None
    MemorySaver = None


# Get project directories
def _get_dirs():
    """Get project directories for storage"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(script_dir)
    project_dir = os.path.dirname(src_dir)
    data_dir = os.path.join(project_dir, ".bharat_data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def create_sqlite_checkpointer(db_path: Optional[str] = None):
    """
    Create a SqliteSaver checkpointer.

    Args:
        db_path: Optional path to SQLite database

    Returns:
        SqliteSaver instance or None if not available
    """
    if not LANGGRAPH_AVAILABLE:
        return None

    if not db_path:
        data_dir = _get_dirs()
        db_path = os.path.join(data_dir, "checkpoints.db")

    try:
        # Create SQLite checkpointer
        checkpointer = SqliteSaver.from_conn_string(db_path)
        return checkpointer
    except Exception as e:
        print(f"Warning: Could not create SQLite checkpointer: {e}")
        return None


def create_memory_checkpointer():
    """
    Create an in-memory checkpointer.

    Returns:
        MemorySaver instance or None if not available
    """
    if not LANGGRAPH_AVAILABLE:
        return None

    try:
        return MemorySaver()
    except Exception as e:
        print(f"Warning: Could not create memory checkpointer: {e}")
        return None


# Default checkpointer factory
_default_checkpointer: Optional[Any] = None


def get_default_checkpointer():
    """
    Get or create the default checkpointer.
    """
    global _default_checkpointer
    if _default_checkpointer is None and LANGGRAPH_AVAILABLE:
        _default_checkpointer = create_memory_checkpointer()
    return _default_checkpointer


class LongTermMemory:
    """
    Long-term memory using JSON file storage.
    Wraps existing ProjectMemory.
    """

    def __init__(self, memory_file: Optional[str] = None):
        if not memory_file:
            data_dir = _get_dirs()
            memory_file = os.path.join(data_dir, "longterm_memory.json")

        self.memory_file = memory_file
        self.memory = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "projects": {},
            "knowledge": {},
            "patterns": {},
            "learning_log": [],
        }

    def _save_memory(self):
        """Save memory to file"""
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def add_project(self, name: str, data: Dict[str, Any]):
        """Add a project to memory"""
        self.memory["projects"][name] = {
            **data,
            "timestamp": self._get_timestamp(),
        }
        self._save_memory()

    def get_project(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a project from memory"""
        return self.memory["projects"].get(name)

    def list_projects(self) -> List[str]:
        """List all projects in memory"""
        return list(self.memory["projects"].keys())

    def add_knowledge(self, category: str, topic: str, data: Any):
        """Add knowledge to memory"""
        if category not in self.memory["knowledge"]:
            self.memory["knowledge"][category] = {}

        self.memory["knowledge"][category][topic] = {
            "data": data,
            "timestamp": self._get_timestamp(),
        }
        self._save_memory()

    def get_knowledge(self, category: str, topic: Optional[str] = None) -> Any:
        """Get knowledge from memory"""
        if topic is None:
            return self.memory["knowledge"].get(category, {})

        category_data = self.memory["knowledge"].get(category, {})
        return category_data.get(topic, {}).get("data")

    def log_learning(self, event_type: str, data: Dict[str, Any]):
        """Log a learning event"""
        self.memory["learning_log"].append({
            "event_type": event_type,
            "data": data,
            "timestamp": self._get_timestamp(),
        })
        self._save_memory()

    def add_pattern(self, pattern_name: str, pattern_data: Dict[str, Any]):
        """Add a learned pattern"""
        self.memory["patterns"][pattern_name] = {
            **pattern_data,
            "timestamp": self._get_timestamp(),
        }
        self._save_memory()

    def get_pattern(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """Get a learned pattern"""
        return self.memory["patterns"].get(pattern_name)

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Singleton for long-term memory
_longterm_memory: Optional[LongTermMemory] = None


def get_longterm_memory() -> LongTermMemory:
    """Get or create long-term memory instance"""
    global _longterm_memory
    if _longterm_memory is None:
        _longterm_memory = LongTermMemory()
    return _longterm_memory


# Import existing ProjectMemory for backward compatibility
def get_project_memory():
    """Get existing ProjectMemory for backward compatibility"""
    try:
        from agents.autonomous_expert import ProjectMemory
        return ProjectMemory()
    except ImportError:
        return None


__all__ = [
    "create_sqlite_checkpointer",
    "create_memory_checkpointer",
    "get_default_checkpointer",
    "LongTermMemory",
    "get_longterm_memory",
    "get_project_memory",
    "LANGGRAPH_AVAILABLE",
]
