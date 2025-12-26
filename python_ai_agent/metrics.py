"""
Metrics Module - Tracks analytics for the AI service
Provides in-memory metrics with optional persistence
"""
import time
from datetime import datetime
from collections import defaultdict
from threading import Lock

class MetricsCollector:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize metrics storage"""
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_response_time_ms": 0,
            "requests_by_intent": defaultdict(int),
            "requests_by_store": defaultdict(int),
            "errors_by_type": defaultdict(int),
            "hourly_requests": defaultdict(int),
            "start_time": datetime.now().isoformat()
        }
        self._request_times = []  # For percentile calculations
    
    def record_request(self, store_id: str, success: bool, response_time_ms: float, 
                       intent: str = None, error_type: str = None, cache_hit: bool = False):
        """Record a single request's metrics"""
        with self._lock:
            self.metrics["total_requests"] += 1
            self.metrics["total_response_time_ms"] += response_time_ms
            self.metrics["requests_by_store"][store_id] += 1
            
            # Track hourly distribution
            hour_key = datetime.now().strftime("%Y-%m-%d %H:00")
            self.metrics["hourly_requests"][hour_key] += 1
            
            if success:
                self.metrics["successful_requests"] += 1
            else:
                self.metrics["failed_requests"] += 1
                if error_type:
                    self.metrics["errors_by_type"][error_type] += 1
            
            if intent:
                self.metrics["requests_by_intent"][intent] += 1
            
            if cache_hit:
                self.metrics["cache_hits"] += 1
            else:
                self.metrics["cache_misses"] += 1
            
            # Store response times for percentile calculation (keep last 1000)
            self._request_times.append(response_time_ms)
            if len(self._request_times) > 1000:
                self._request_times.pop(0)
    
    def get_metrics(self) -> dict:
        """Return current metrics snapshot"""
        with self._lock:
            total = self.metrics["total_requests"]
            avg_response_time = (
                self.metrics["total_response_time_ms"] / total if total > 0 else 0
            )
            
            # Calculate percentiles
            p50, p95, p99 = 0, 0, 0
            if self._request_times:
                sorted_times = sorted(self._request_times)
                n = len(sorted_times)
                p50 = sorted_times[int(n * 0.5)] if n > 0 else 0
                p95 = sorted_times[int(n * 0.95)] if n > 0 else 0
                p99 = sorted_times[int(n * 0.99)] if n > 0 else 0
            
            cache_total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
            cache_hit_rate = (
                self.metrics["cache_hits"] / cache_total * 100 if cache_total > 0 else 0
            )
            
            success_rate = (
                self.metrics["successful_requests"] / total * 100 if total > 0 else 0
            )
            
            return {
                "summary": {
                    "total_requests": total,
                    "successful_requests": self.metrics["successful_requests"],
                    "failed_requests": self.metrics["failed_requests"],
                    "success_rate_percent": round(success_rate, 2),
                    "cache_hit_rate_percent": round(cache_hit_rate, 2),
                    "uptime_since": self.metrics["start_time"]
                },
                "response_times": {
                    "average_ms": round(avg_response_time, 2),
                    "p50_ms": round(p50, 2),
                    "p95_ms": round(p95, 2),
                    "p99_ms": round(p99, 2)
                },
                "breakdown": {
                    "by_intent": dict(self.metrics["requests_by_intent"]),
                    "by_store": dict(self.metrics["requests_by_store"]),
                    "by_error_type": dict(self.metrics["errors_by_type"]),
                    "hourly": dict(list(self.metrics["hourly_requests"].items())[-24:])
                }
            }
    
    def reset(self):
        """Reset all metrics (useful for testing)"""
        with self._lock:
            self._initialize()


# Singleton instance
metrics = MetricsCollector()
