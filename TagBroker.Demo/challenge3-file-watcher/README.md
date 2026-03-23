# Challenge 3: File System Watcher & Reporter

Monitors a directory for file changes and reports statistics periodically using the watchdog library.

## Requirements

```bash
pip install watchdog
```

## Features

- Watches directory for file events (create, modify, delete)
- Logs events in real-time
- Prints summary report every minute
- Configurable via config.json
- Clean shutdown with final summary

## Usage

```bash
python file_watcher.py
```

Press Ctrl+C to stop.

## Configuration

Edit `config.json`:

```json
{
  "watch_path": "./watch",
  "scan_interval": 5,
  "summary_interval": 60
}
```

- `watch_path` - Directory to monitor
- `scan_interval` - How often to scan (seconds)
- `summary_interval` - How often to print summary (seconds)

## Example Output

```
Watching directory: ./watch
Scan interval: 5s
Summary interval: 60s

[2024-03-23 10:30:15] CREATE: file1.txt
[2024-03-23 10:30:20] MODIFY: file1.txt
[2024-03-23 10:30:25] DELETE: file1.txt

--- Summary at 2024-03-23 10:31:15 ---
Created: 1
Modified: 1
Deleted: 1
----------------------------
```

## Design Focus

- Using watchdog library for file system monitoring
- Observer pattern (watchdog events)
- Configuration management
- Thread-safe event logging
- Clean shutdown handling
