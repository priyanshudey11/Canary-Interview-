## Challenge 1: Task Tracker

A command-line to-do app with persistent storage.

Location: `challenge1-task-tracker/`

Focus: Structure, error handling, separation of concerns

```bash
cd challenge1-task-tracker
python task_tracker.py
```

## Challenge 2: CSV Data Processor

Process CSV files with filter, select, and sort operations.

Location: `challenge2-csv-processor/`

Focus: Strategy pattern, modularity, testing

```bash
cd challenge2-csv-processor
python csv_processor.py sample_data.csv "filter age > 28 | select name,city | sort age desc"
```

## Challenge 3: File System Watcher

Monitor a directory for file changes with periodic reporting.

Location: `challenge3-file-watcher/`

Focus: Observer pattern, config, clean shutdown

```bash
cd challenge3-file-watcher
python file_watcher.py
```

## Challenge 4: Parking Lot System

Multi-floor parking lot with different vehicle types and pricing.

Location: `challenge4-parking-lot/`

Focus: Class design, Factory/Strategy patterns, extensibility

```bash
cd challenge4-parking-lot
python parking_lot.py
```

## Requirements

Python 3.7+ required.

Install dependencies:
```bash
pip install pandas watchdog
```

Or use requirements.txt in each challenge folder.
