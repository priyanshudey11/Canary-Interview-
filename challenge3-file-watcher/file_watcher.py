import json
import time
import threading
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class EventTracker(FileSystemEventHandler):
    def __init__(self):
        self.events = []
        self.lock = threading.Lock()

    def on_created(self, event):
        if not event.is_directory:
            self._log_event('create', event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._log_event('modify', event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self._log_event('delete', event.src_path)

    def _log_event(self, event_type, filepath):
        import os
        filename = os.path.basename(filepath)

        with self.lock:
            event_data = {
                'type': event_type,
                'filename': filename,
                'timestamp': datetime.now()
            }
            self.events.append(event_data)

            timestamp = event_data['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {event_type.upper()}: {filename}")

    def get_summary(self):
        with self.lock:
            summary = {'create': 0, 'modify': 0, 'delete': 0}
            for event in self.events:
                summary[event['type']] += 1
            return summary

    def clear_events(self):
        with self.lock:
            self.events = []


class Config:
    @staticmethod
    def load(config_file='config.json'):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_file} not found, using defaults")
            return {
                'watch_path': './watch',
                'summary_interval': 60
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing config: {e}")
            return None


class FileWatcherApp:
    def __init__(self, config):
        self.config = config
        self.event_handler = EventTracker()
        self.observer = Observer()
        self.running = False
        self.summary_thread = None

    def start(self):
        import os

        watch_path = self.config['watch_path']

        if not os.path.exists(watch_path):
            try:
                os.makedirs(watch_path)
                print(f"Created watch directory: {watch_path}")
            except Exception as e:
                print(f"Error creating directory: {e}")
                return

        self.running = True
        self.observer.schedule(self.event_handler, watch_path, recursive=False)
        self.observer.start()

        self.summary_thread = threading.Thread(target=self._summary_loop, daemon=True)
        self.summary_thread.start()

        print(f"Watching directory: {watch_path}")
        print(f"Summary interval: {self.config['summary_interval']}s")

    def _summary_loop(self):
        while self.running:
            time.sleep(self.config['summary_interval'])
            if self.running:
                self._print_summary()

    def _print_summary(self):
        summary = self.event_handler.get_summary()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n--- Summary at {timestamp} ---")
        print(f"Created: {summary['create']}")
        print(f"Modified: {summary['modify']}")
        print(f"Deleted: {summary['delete']}")

    def stop(self):
        print("\nShutting down...")
        self.running = False
        self.observer.stop()
        self.observer.join()

        if self.summary_thread:
            self.summary_thread.join(timeout=2)

        self._print_summary()
        print("Shutdown complete")


def main():
    config = Config.load()
    if not config:
        return

    app = FileWatcherApp(config)

    try:
        app.start()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        app.stop()


if __name__ == "__main__":
    main()
