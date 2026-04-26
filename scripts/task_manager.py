#!/usr/bin/env python3
"""Task Manager - Dynamic task tracking system for StenoMD project."""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
TASKS_DIR = PROJECT_ROOT / "vault" / "tasks"
UNFINISHED_FILE = PROJECT_ROOT / "Unfinished-tasks.md"
COMPLETED_FILE = PROJECT_ROOT / "Completed-tasks.md"

# Status values
STATUS_DEFERRED = "DEFERRED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_READY = "READY_TO_START"
STATUS_COMPLETED = "COMPLETED"

# Priority values
PRIORITY_CRITICAL = 100
PRIORITY_HIGH = 75
PRIORITY_MEDIUM = 50
PRIORITY_LOW = 25

PRIORITY_MAP = {
    "CRITICAL": PRIORITY_CRITICAL,
    "HIGH": PRIORITY_HIGH,
    "MEDIUM": PRIORITY_MEDIUM,
    "LOW": PRIORITY_LOW,
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Task:
    """Task data class."""
    id: str
    title: str
    status: str
    priority: str
    created: str
    last_checked: str
    phase_reference: str
    instructions: str
    dependencies: List[str]
    expected_output: str
    blocked_by: str
    notes: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# TASK MANAGER
# ============================================================================

class TaskManager:
    """Task Manager for StenoMD project."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else PROJECT_ROOT
        self.unfinished_file = self.project_root / "Unfinished-tasks.md"
        self.completed_file = self.project_root / "Completed-tasks.md"
        self.tasks_dir = self.project_root / "vault" / "tasks"
        
        # Ensure directories exist
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
    
    # ------------------------------------------------------------------------
    # READING TASKS
    # ------------------------------------------------------------------------
    
    def read_tasks_markdown(self) -> str:
        """Read the unfinished tasks file."""
        if self.unfinished_file.exists():
            return self.unfinished_file.read_text()
        return ""
    
    def parse_task(self, task_section: str) -> Optional[Task]:
        """Parse a single task from markdown text."""
        lines = task_section.strip().split('\n')
        
        data = {
            'id': '',
            'title': '',
            'status': STATUS_DEFERRED,
            'priority': 'HIGH',
            'created': datetime.now().strftime("%Y-%m-%d"),
            'last_checked': datetime.now().strftime("%Y-%m-%d"),
            'phase_reference': '',
            'instructions': '',
            'dependencies': [],
            'expected_output': '',
            'blocked_by': '',
            'notes': '',
        }
        
        for line in lines:
            line = line.strip()
            
            # Parse header - only first line of section
            # Format: "### Task ###: Title" or just "Title"
            if not data['title']:
                # Try to match header line format
                header_match = re.match(r'^(?:### Task \d+: )?(.+)$', line)
                if header_match:
                    potential_title = header_match.group(1).strip()
                    if potential_title:
                        data['title'] = potential_title
            
            # Parse fields (**Field:** value)
            field_match = re.match(r'^\*\*([A-Za-z ]+):\*\* (.+)$', line)
            if field_match:
                key = field_match.group(1).lower().strip()
                value = field_match.group(2).strip()
                
                # Map to data dict
                key_map = {
                    'id': 'id',
                    'status': 'status', 
                    'priority': 'priority',
                    'created': 'created',
                    'last checked': 'last_checked',
                    'phase reference': 'phase_reference',
                    'instructions': 'instructions',
                    'dependencies': 'dependencies',
                    'expected output': 'expected_output',
                    'blocked by': 'blocked_by',
                    'notes': 'notes',
                }
                
                if key in key_map:
                    mapped_key = key_map[key]
                    if mapped_key == 'dependencies':
                        # Handle list format
                        data['dependencies'] = [v.strip() for v in value.split(',') if v.strip() and v.strip() != 'None']
                    else:
                        # Only set if not already set (ignore template values)
                        if not data[mapped_key] or '<' in data[mapped_key]:
                            data[mapped_key] = value
        
        # Validate - must have an ID
        if not data['id']:
            return None
        
        return Task(**data)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks from unfinished file."""
        content = self.read_tasks_markdown()
        
        # Use finditer for better accuracy
        tasks = []
        task_starts = list(re.finditer(r'^\s*### Task \d+: ', content, flags=re.MULTILINE))
        
        for i, match in enumerate(task_starts):
            start = match.end()
            # End is next task or start of next major section (##)
            if i+1 < len(task_starts):
                end = task_starts[i+1].start()
            else:
                # Find next ## marker after this position
                marker_match = re.search(r'^\n## ', content[start:], re.MULTILINE)
                if marker_match:
                    end = start + marker_match.start()
                else:
                    end = len(content)
            section = content[start:end].strip()
            
            task = self.parse_task(section)
            if task:
                # Skip tasks with placeholder patterns in ID or status
                if '###' in task.id or task.status.startswith('<'):
                    continue
                tasks.append(task)
        
        return tasks
    
    def get_pending_tasks(self, status: str = None) -> List[Task]:
        """Get pending tasks."""
        all_tasks = self.get_all_tasks()
        
        if status:
            return [t for t in all_tasks if t.status == status]
        
        return [t for t in all_tasks if t.status != STATUS_COMPLETED]
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a specific task by ID."""
        all_tasks = self.get_all_tasks()
        for task in all_tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_next_task(self) -> Optional[Task]:
        """Get the next task to work on."""
        pending = self.get_pending_tasks()
        
        ready = [t for t in pending if t.status == STATUS_READY]
        in_progress = [t for t in pending if t.status == STATUS_IN_PROGRESS]
        deferred = [t for t in pending if t.status == STATUS_DEFERRED]
        
        for group in [ready, in_progress, deferred]:
            group.sort(key=lambda t: PRIORITY_MAP.get(t.priority, 50), reverse=True)
        
        if ready:
            return ready[0]
        if in_progress:
            return in_progress[0]
        if deferred:
            return deferred[0]
        
        return None
    
    # ------------------------------------------------------------------------
    # UPDATING TASKS
    # ------------------------------------------------------------------------
    
    def _update_task_in_file(self, task_id: str, field: str, new_value: str) -> bool:
        """Update a specific field for a task."""
        if not self.unfinished_file.exists():
            return False
        
        content = self.read_tasks_markdown()
        
        # Build the pattern to find the field within the task section
        new_lines = []
        in_task = False
        updated = False
        
        for line in content.split('\n'):
            # Check if we're in the target task section
            if f'**ID:** {task_id}' in line:
                in_task = True
            
            if in_task:
                # Try to replace the field
                old_field = f'**{field}:**'
                if old_field in line:
                    # Find the value after **field:**
                    match = re.match(r'^(\*\*' + re.escape(field) + r':\*\* )(.+)$', line)
                    if match:
                        new_lines.append(match.group(1) + new_value)
                        updated = True
                        in_task = False  # Stop updating after first match
                        continue
                    
                    # Try simpler replacement
                    new_line = re.sub(r'\*\*' + re.escape(field) + r':\*\* .+', 
                                    f'**{field}:** {new_value}', line)
                    if new_line != line:
                        new_lines.append(new_line)
                        updated = True
                        in_task = False
                        continue
            
            # Stop at next task section
            if in_task and line.startswith('## '):
                in_task = False
            
            new_lines.append(line)
        
        if updated:
            self.unfinished_file.write_text('\n'.join(new_lines))
        
        return updated
    
    def mark_in_progress(self, task_id: str) -> bool:
        """Mark task as in progress."""
        return self._update_task_in_file(task_id, 'Status', STATUS_IN_PROGRESS)
    
    def mark_ready(self, task_id: str) -> bool:
        """Mark task as ready to start."""
        return self._update_task_in_file(task_id, 'Status', STATUS_READY)
    
    def mark_deferred(self, task_id: str) -> bool:
        """Mark task as deferred."""
        return self._update_task_in_file(task_id, 'Status', STATUS_DEFERRED)
    
    def mark_completed(self, task_id: str, notes: str = "") -> bool:
        """Mark task as completed and move to history."""
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        
        self._add_to_completed(task, notes)
        self._update_task_in_file(task_id, 'Status', STATUS_COMPLETED)
        
        return True
    
    def update_status(self, task_id: str, new_status: str, notes: str = "") -> bool:
        """Update task status."""
        if new_status == STATUS_COMPLETED:
            return self.mark_completed(task_id, notes)
        elif new_status == STATUS_IN_PROGRESS:
            return self.mark_in_progress(task_id)
        elif new_status == STATUS_READY:
            return self.mark_ready(task_id)
        elif new_status == STATUS_DEFERRED:
            return self.mark_deferred(task_id)
        return False
    
    # ------------------------------------------------------------------------
    # COMPLETED TASKS
    # ------------------------------------------------------------------------
    
    def _init_completed_file(self) -> None:
        """Initialize completed tasks file."""
        if not self.completed_file.exists():
            header = f"""# StenoMD Completed Tasks

**Last Updated:** {datetime.now().strftime("%Y-%m-%d")}

---

## COMPLETED TASKS

*No completed tasks yet.*

---

## HISTORY

| ID | Title | Completed | Notes |
|----|-------|-----------|--------|
| | | | |

---
*History of completed tasks.*
"""
            self.completed_file.write_text(header)
    
    def _add_to_completed(self, task: Task, notes: str = "") -> None:
        """Add completed task to history."""
        self._init_completed_file()
        
        existing = ""
        if self.completed_file.exists():
            existing = self.completed_file.read_text()
        
        completion_date = datetime.now().strftime("%Y-%m-%d")
        
        new_entry = f"""
### {task.id}: {task.title}
**Completed:** {completion_date}  
**Original Priority:** {task.priority}

**Notes:** {notes}

---
"""
        
        # Insert after header
        parts = existing.split('## COMPLETED TASKS\n\n', 1)
        if len(parts) == 2:
            new_content = parts[0] + '## COMPLETED TASKS\n\n' + new_entry + parts[1]
        else:
            new_content = existing + new_entry
        
        self.completed_file.write_text(new_content)
    
    def get_completed_tasks(self) -> List[Dict]:
        """Get completed tasks."""
        if not self.completed_file.exists():
            return []
        
        content = self.completed_file.read_text()
        
        tasks = []
        sections = re.split(r'^### ', content, flags=re.MULTILINE)
        
        for section in sections:
            if not section.strip() or 'COMPLETED TASKS' in section or 'HISTORY' in section:
                continue
            
            lines = section.split('\n')
            task_info = {'id': '', 'title': '', 'completed': '', 'notes': ''}
            
            for line in lines:
                if ':**' in line:
                    parts = line.split(':**', 1)
                    if len(parts) == 2:
                        key = parts[0].strip().replace('**', '').lower()
                        value = parts[1].strip()
                        if key in task_info:
                            task_info[key] = value
            
            if task_info.get('id'):
                tasks.append(task_info)
        
        return tasks
    
    # ------------------------------------------------------------------------
    # PLANNER INTEGRATION
    # ------------------------------------------------------------------------
    
    def check_dependencies(self, task_id: str) -> Dict:
        """Check if task dependencies are met."""
        task = self.get_task_by_id(task_id)
        if not task:
            return {'ready': False, 'reason': 'Task not found'}
        
        dep_status = []
        all_met = True
        
        for dep in task.dependencies:
            dep_match = re.match(r'TASK-\d+', dep)
            if dep_match:
                dep_id = dep_match.group()
                dep_task = self.get_task_by_id(dep_id)
                
                if dep_task:
                    if dep_task.status == STATUS_COMPLETED:
                        dep_status.append({'id': dep_id, 'met': True})
                    else:
                        dep_status.append({'id': dep_id, 'met': False, 'status': dep_task.status})
                        all_met = False
        
        return {'ready': all_met, 'dependencies': dep_status, 'task': task.id}
    
    def suggest_next_action(self) -> str:
        """Suggest next action."""
        next_task = self.get_next_task()
        
        if not next_task:
            return "No pending tasks."
        
        dep_check = self.check_dependencies(next_task.id)
        
        if next_task.status == STATUS_READY and dep_check['ready']:
            return f"READY: {next_task.id} - {next_task.title}"
        elif next_task.status == STATUS_IN_PROGRESS:
            return f"CONTINUE: {next_task.id} - {next_task.title}"
        elif next_task.status == STATUS_DEFERRED:
            return f"DEFERRED: {next_task.id} - {next_task.title}"
        
        return f"Task: {next_task.id} - {next_task.title} ({next_task.status})"
    
    def generate_startup_report(self) -> str:
        """Generate report for planner startup."""
        pending = self.get_pending_tasks()
        
        ready = [t for t in pending if t.status == STATUS_READY]
        in_progress = [t for t in pending if t.status == STATUS_IN_PROGRESS]
        deferred = [t for t in pending if t.status == STATUS_DEFERRED]
        
        report = f"""# Task Manager Report
Generated: {datetime.now().isoformat()}

## Summary
- Total Pending: {len(pending)}
- Ready: {len(ready)}
- In Progress: {len(in_progress)}
- Deferred: {len(deferred)}

## Next Action
{self.suggest_next_action()}
"""
        
        if in_progress:
            report += "\n## Working On\n"
            for t in in_progress:
                report += f"- {t.id}: {t.title}\n"
        
        if deferred:
            report += "\n## Deferred\n"
            for t in deferred[:3]:
                report += f"- {t.id}: {t.title} ({t.priority})\n"
        
        return report


# ============================================================================
# MAIN
# ============================================================================

def main():
    """CLI for task manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Task Manager")
    parser.add_argument('--list', action='store_true', help='List pending tasks')
    parser.add_argument('--next', action='store_true', help='Show next task')
    parser.add_argument('--update', type=str, help='Update: ID:STATUS')
    parser.add_argument('--check-deps', type=str, help='Check dependencies')
    parser.add_argument('--startup-report', action='store_true', help='Generate startup report')
    parser.add_argument('--all', action='store_true', help='List all tasks')
    
    args = parser.parse_args()
    
    tm = TaskManager()
    
    if args.list or args.all:
        tasks = tm.get_all_tasks() if args.all else tm.get_pending_tasks()
        if not tasks:
            print("No tasks." if args.list else "No pending tasks.")
        else:
            for t in tasks:
                print(f"[{t.status}] {t.id}: {t.title} (priority: {t.priority})")
    
    elif args.next:
        task = tm.get_next_task()
        if task:
            print(f"{task.id}: {task.title}")
            print(f"  Status: {task.status}, Priority: {task.priority}")
        else:
            print("No pending tasks.")
    
    elif args.update:
        if ':' not in args.update:
            print("Use format: ID:STATUS (e.g., TASK-001:IN_PROGRESS)")
        else:
            task_id, status = args.update.split(':', 1)
            success = tm.update_status(task_id, status)
            print(f"Updated {task_id}: {success}")
    
    elif args.check_deps:
        result = tm.check_dependencies(args.check_deps)
        print(json.dumps(result, indent=2))
    
    elif args.startup_report:
        print(tm.generate_startup_report())
    
    else:
        print("Task Manager")
        print("Options: --list, --next, --all, --update, --check-deps, --startup-report")


if __name__ == "__main__":
    main()
