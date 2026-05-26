import secrets
import threading
import time
from collections import deque


class SessionStore:
    def __init__(self, ttl_seconds=8 * 60 * 60):
        self.ttl_seconds = ttl_seconds
        self.sessions = {}
        self.lock = threading.RLock()

    def create(self, username):
        token = secrets.token_urlsafe(24)
        expires_at = time.time() + self.ttl_seconds
        with self.lock:
            self.sessions[token] = {"username": username, "expires_at": expires_at}
        return token

    def get(self, token):
        if not token:
            return None

        now = time.time()
        with self.lock:
            session = self.sessions.get(token)
            if not session:
                return None
            if session["expires_at"] < now:
                self.sessions.pop(token, None)
                return None
            session["expires_at"] = now + self.ttl_seconds
            return session["username"]

    def delete(self, token):
        with self.lock:
            self.sessions.pop(token, None)


class ChatHistoryStore:
    def __init__(self, max_messages_per_user=30):
        self.max_messages_per_user = max_messages_per_user
        self.history = {}
        self.lock = threading.RLock()

    def get(self, username):
        with self.lock:
            return list(self.history.get(username, []))

    def append_pair(self, username, user_message, assistant_message):
        with self.lock:
            messages = self.history.setdefault(username, [])
            messages.append(("user", user_message))
            messages.append(("assistant", assistant_message))
            if len(messages) > self.max_messages_per_user:
                self.history[username] = messages[-self.max_messages_per_user:]

    def clear(self, username):
        with self.lock:
            self.history.pop(username, None)


class TTLCache:
    def __init__(self, ttl_seconds=120, max_entries=128):
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self.items = {}
        self.lock = threading.RLock()

    def get(self, key):
        now = time.time()
        with self.lock:
            item = self.items.get(key)
            if not item:
                return None
            expires_at, value = item
            if expires_at < now:
                self.items.pop(key, None)
                return None
            return value

    def set(self, key, value):
        with self.lock:
            if len(self.items) >= self.max_entries:
                oldest_key = min(self.items, key=lambda item_key: self.items[item_key][0])
                self.items.pop(oldest_key, None)
            self.items[key] = (time.time() + self.ttl_seconds, value)


class RequestLimiter:
    def __init__(self, max_concurrent=4):
        self.semaphore = threading.BoundedSemaphore(max_concurrent)

    def acquire(self, timeout=1):
        return self.semaphore.acquire(timeout=timeout)

    def release(self):
        self.semaphore.release()


class MetricsStore:
    def __init__(self, max_events=2000, window_seconds=300):
        self.max_events = max_events
        self.window_seconds = window_seconds
        self.events = deque(maxlen=max_events)
        self.active_requests = 0
        self.total_started = 0
        self.total_requests = 0
        self.lock = threading.RLock()

    def request_started(self):
        started_at = time.perf_counter()
        with self.lock:
            self.active_requests += 1
            self.total_started += 1
        return started_at

    def request_finished(self, path, method, status_code, started_at):
        duration = time.perf_counter() - started_at
        now = time.time()
        with self.lock:
            self.active_requests = max(0, self.active_requests - 1)
            self.total_requests += 1
            self.events.append(
                {
                    "timestamp": now,
                    "path": path,
                    "method": method,
                    "status": status_code,
                    "duration": duration,
                }
            )
            self._prune(now)

    def snapshot(self):
        now = time.time()
        with self.lock:
            self._prune(now)
            events = list(self.events)
            active_requests = self.active_requests
            total_started = self.total_started
            total_requests = self.total_requests

        durations = [event["duration"] for event in events]
        errors = [event for event in events if event["status"] >= 500]
        client_errors = [event for event in events if 400 <= event["status"] < 500]
        path_counts = {}
        for event in events:
            path_counts[event["path"]] = path_counts.get(event["path"], 0) + 1

        elapsed = self.window_seconds
        if events:
            elapsed = max(1, now - min(event["timestamp"] for event in events))

        return {
            "active_requests": active_requests,
            "total_started": total_started,
            "total_requests": total_requests,
            "window_requests": len(events),
            "rps": len(events) / elapsed if elapsed else 0,
            "avg_latency": sum(durations) / len(durations) if durations else 0,
            "p95_latency": self._percentile(durations, 0.95),
            "max_latency": max(durations) if durations else 0,
            "server_error_rate": len(errors) / len(events) if events else 0,
            "client_error_rate": len(client_errors) / len(events) if events else 0,
            "path_counts": sorted(path_counts.items(), key=lambda item: item[1], reverse=True)[:8],
        }

    def _prune(self, now):
        cutoff = now - self.window_seconds
        while self.events and self.events[0]["timestamp"] < cutoff:
            self.events.popleft()

    def _percentile(self, values, percentile):
        if not values:
            return 0
        ordered = sorted(values)
        index = min(len(ordered) - 1, max(0, int(len(ordered) * percentile) - 1))
        return ordered[index]
