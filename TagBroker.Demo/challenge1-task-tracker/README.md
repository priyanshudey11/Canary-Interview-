# Challenge 1: Task Tracker

A simple command-line to-do app with persistent storage.

## Features

- Add tasks
- List all tasks
- Mark tasks as complete
- Delete tasks
- Saves to tasks.json

## Usage

```bash
python task_tracker.py
```

## Commands

```
add Buy milk          # Add a new task
list                  # Show all tasks
complete 1            # Mark task 1 as complete
delete 2              # Delete task 2
quit                  # Exit the app
```

## Design Focus

- Separation of concerns (Task, TaskStorage, TaskTracker)
- Error handling for invalid inputs
- Clean class structure
