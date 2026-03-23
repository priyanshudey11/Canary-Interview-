import json
import os
from datetime import datetime


class Task:
    def __init__(self, id, description, completed=False, created_at=None):
        self.id = id
        self.description = description
        self.completed = completed
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data):
        return Task(
            data['id'],
            data['description'],
            data['completed'],
            data['created_at']
        )


class TaskStorage:
    def __init__(self, filename='tasks.json'):
        self.filename = filename

    def load(self):
        if not os.path.exists(self.filename):
            return []

        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return [Task.from_dict(task) for task in data]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading tasks: {e}")
            return []

    def save(self, tasks):
        try:
            with open(self.filename, 'w') as f:
                json.dump([task.to_dict() for task in tasks], f, indent=2)
        except IOError as e:
            print(f"Error saving tasks: {e}")


class TaskTracker:
    def __init__(self, storage):
        self.storage = storage
        self.tasks = storage.load()

    def add_task(self, description):
        if not description or not description.strip():
            raise ValueError("Task description cannot be empty")

        next_id = max([task.id for task in self.tasks], default=0) + 1
        task = Task(next_id, description.strip())
        self.tasks.append(task)
        self.storage.save(self.tasks)
        return task

    def list_tasks(self):
        return self.tasks

    def complete_task(self, task_id):
        task = self._find_task(task_id)
        if task.completed:
            raise ValueError(f"Task {task_id} is already completed")
        task.completed = True
        self.storage.save(self.tasks)
        return task

    def delete_task(self, task_id):
        task = self._find_task(task_id)
        self.tasks.remove(task)
        self.storage.save(self.tasks)
        return task

    def _find_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise ValueError(f"Task {task_id} not found")


def main():
    storage = TaskStorage()
    tracker = TaskTracker(storage)

    print("Task Tracker")
    print("Commands: add <description> | list | complete <id> | delete <id> | quit")

    while True:
        try:
            command = input("\n> ").strip()

            if not command:
                continue

            parts = command.split(maxsplit=1)
            action = parts[0].lower()

            if action == "quit" or action == "exit":
                break

            elif action == "add":
                if len(parts) < 2:
                    print("Error: Please provide a task description")
                    continue
                task = tracker.add_task(parts[1])
                print(f"Added task {task.id}: {task.description}")

            elif action == "list":
                tasks = tracker.list_tasks()
                if not tasks:
                    print("No tasks")
                else:
                    for task in tasks:
                        status = "✓" if task.completed else " "
                        print(f"[{status}] {task.id}. {task.description}")

            elif action == "complete":
                if len(parts) < 2:
                    print("Error: Please provide a task ID")
                    continue
                task_id = int(parts[1])
                task = tracker.complete_task(task_id)
                print(f"Completed task {task_id}: {task.description}")

            elif action == "delete":
                if len(parts) < 2:
                    print("Error: Please provide a task ID")
                    continue
                task_id = int(parts[1])
                task = tracker.delete_task(task_id)
                print(f"Deleted task {task_id}: {task.description}")

            else:
                print(f"Unknown command: {action}")

        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()
