import time
from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime


class MetricsService:
    """
    Metrics service for tracking performance, mis-triage, and bias
    Singleton pattern for global access
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsService, cls).__new__(cls)
            cls._instance.metrics = defaultdict(int)
            cls._instance.latency_data: Dict[str, List[float]] = defaultdict(list)
            cls._instance.traces: List[Dict[str, Any]] = []
            cls._instance.mistriage_count = 0
            cls._instance.bias_detected_count = 0
        return cls._instance

    def log_latency(self, component: str, start_time: float) -> None:
        """
        Log latency for a component
        
        Args:
            component: Component name
            start_time: Start timestamp
        """
        duration = time.time() - start_time
        self.metrics[f"{component}_latency_sum"] += duration
        self.metrics[f"{component}_count"] += 1
        self.latency_data[component].append(duration)
        
        # Keep only last 100 measurements per component
        if len(self.latency_data[component]) > 100:
            self.latency_data[component] = self.latency_data[component][-100:]

    def log_mistriage(self) -> None:
        """Log a potential mis-triage event"""
        self.mistriage_count += 1
        self.metrics["mis_triage_potential"] += 1

    def log_bias_check(self, detected: bool) -> None:
        """
        Log bias detection result
        
        Args:
            detected: Whether bias was detected
        """
        if detected:
            self.bias_detected_count += 1
            self.metrics["bias_detected_count"] += 1
        self.metrics["bias_checks_total"] += 1

    def get_average_latency(self, component: str) -> float:
        """
        Get average latency for a component
        
        Args:
            component: Component name
            
        Returns:
            Average latency in seconds
        """
        if component not in self.latency_data or not self.latency_data[component]:
            return 0.0
        return sum(self.latency_data[component]) / len(self.latency_data[component])

    def get_report(self) -> Dict[str, Any]:
        """
        Get comprehensive metrics report
        
        Returns:
            Dictionary with metrics, averages, and counts
        """
        # Calculate average latencies
        avg_latencies = {}
        for component in self.latency_data:
            avg_latencies[component] = self.get_average_latency(component)
        
        return {
            "metrics": dict(self.metrics),
            "average_latencies": avg_latencies,
            "mistriage_count": self.mistriage_count,
            "bias_detected_count": self.bias_detected_count,
            "trace_count": len(self.traces),
            "timestamp": datetime.now().isoformat()
        }

    def reset(self) -> None:
        """Reset all metrics (useful for testing)"""
        self.metrics.clear()
        self.latency_data.clear()
        self.traces.clear()
        self.mistriage_count = 0
        self.bias_detected_count = 0


# Singleton instance
metrics_service = MetricsService()