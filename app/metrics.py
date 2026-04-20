from __future__ import annotations

import time
from collections import Counter
from statistics import mean
from .logging_config import get_logger

log = get_logger()

# Internal state
REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
QUALITY_SCORES: list[float] = []
ERRORS: Counter[str] = Counter()
TRAFFIC: int = 0
ALERTS: list[dict] = []

# History for charts (limit to last 50 points)
HISTORY: list[dict] = []
MAX_HISTORY = 50

def record_request(latency_ms: int, cost_usd: float, tokens_in: int, tokens_out: int, quality_score: float) -> None:
    global TRAFFIC
    TRAFFIC += 1
    REQUEST_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append(cost_usd)
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    QUALITY_SCORES.append(quality_score)
    
    # Simple real-time alerting check
    if cost_usd > 0.01: # Single request cost spike
        log.warning(
            "alert_triggered",
            name="cost_budget_spike",
            severity="P3",
            current_value=cost_usd,
            threshold=0.01,
            msg="Single request cost is too high!"
        )
        ALERTS.append({
            "ts": time.time(),
            "name": "cost_budget_spike",
            "severity": "P3",
            "msg": "Single request cost is too high!"
        })
    
    total_cost = sum(REQUEST_COSTS)
    if total_cost > 0.1: # Total session cost budget
        log.error(
            "alert_triggered",
            name="total_budget_exceeded",
            severity="P1",
            current_value=total_cost,
            threshold=0.1,
            msg="Total budget for this session has been exceeded!"
        )
        # Avoid duplicate alerts for the same condition
        if not any(a["name"] == "total_budget_exceeded" for a in ALERTS[-5:]):
            ALERTS.append({
                "ts": time.time(),
                "name": "total_budget_exceeded",
                "severity": "P1",
                "msg": f"Total budget exceeded: ${total_cost:.4f}"
            })

    if latency_ms > 2000: # High latency check
        if not any(a["name"] == "high_latency_p95" for a in ALERTS[-3:]):
            ALERTS.append({
                "ts": time.time(),
                "name": "high_latency_p95",
                "severity": "P2",
                "msg": f"High latency detected: {latency_ms}ms"
            })
            log.warning("alert_triggered", name="high_latency_p95", severity="P2", latency=latency_ms)
    
    if len(ALERTS) > 10:
        ALERTS.pop(0)
    
    # Update history point
    HISTORY.append({
        "timestamp": time.time(),
        "latency": latency_ms,
        "cost": cost_usd,
        "tokens": tokens_in + tokens_out,
        "quality": quality_score
    })
    if len(HISTORY) > MAX_HISTORY:
        HISTORY.pop(0)


def record_error(error_type: str) -> None:
    global TRAFFIC
    ERRORS[error_type] += 1
    
    # Calculate error rate
    total_errors = sum(ERRORS.values())
    error_rate = (total_errors / TRAFFIC * 100) if TRAFFIC > 0 else 0
    
    if error_rate > 2: # Error Rate Threshold (> 2%)
        if not any(a["name"] == "high_error_rate" for a in ALERTS[-3:]):
            ALERTS.append({
                "ts": time.time(),
                "name": "high_error_rate",
                "severity": "P1",
                "msg": f"Critical error rate: {error_rate:.1f}% ({error_type})"
            })
            log.error("alert_triggered", name="high_error_rate", severity="P1", error_rate=error_rate)

    if len(ALERTS) > 10:
        ALERTS.pop(0)


def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def snapshot() -> dict:
    return {
        "traffic": TRAFFIC,
        "latency_p50": percentile(REQUEST_LATENCIES, 50),
        "latency_p95": percentile(REQUEST_LATENCIES, 95),
        "latency_p99": percentile(REQUEST_LATENCIES, 99),
        "avg_cost_usd": round(mean(REQUEST_COSTS), 4) if REQUEST_COSTS else 0.0,
        "total_cost_usd": round(sum(REQUEST_COSTS), 4),
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),
        "error_breakdown": dict(ERRORS),
        "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
        "history": HISTORY,
        "alerts": ALERTS[::-1], # Newest first
        "slo": {
            "latency_p95_limit": 2000,
            "error_rate_limit": 0.05,
            "quality_min": 0.7
        }
    }
