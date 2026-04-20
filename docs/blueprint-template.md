# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: Antigravity
- [REPO_URL]: https://github.com/vinuni-ai20k/lab13-observability
- [MEMBERS]:
  - Member A: Alice | Role: Logging & PII
  - Member B: Bob | Role: Tracing & Enrichment
  - Member C: Charlie | Role: SLO & Alerts
  - Member D: David | Role: Load Test & Dashboard
  - Member E: Eve | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 246
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: images/correlation_id.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: images/pii_redaction.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: images/trace_waterfall.png
- [TRACE_WATERFALL_EXPLANATION]: One interesting span is the `retrieve` span which shows the latency of the RAG component. By analyzing this span, we can determine if slowness is caused by the vector store or the LLM generation.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: images/dashboard.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 2653ms |
| Error Rate | < 2% | 28d | 0.5% |
| Cost Budget | < $2.5/day | 1d | $0.0014 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: images/alert_rules.png
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#L16-L27]

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: tool_fail
- [SYMPTOMS_OBSERVED]: The Chat API returned a 500 Internal Server Error with the detail "RuntimeError". Users reported unable to get answers from the agent.
- [ROOT_CAUSE_PROVED_BY]: Log line in `data/logs.jsonl`: `{"service": "api", "error_type": "RuntimeError", "payload": {"detail": "Vector store timeout", "message_preview": "test message"}, "event": "request_failed", "correlation_id": "req-ffea2b06"}`. The trace in Langfuse showed the error originated in the `retrieve` span.
- [FIX_ACTION]: Disabled the `tool_fail` incident toggle. In a real-world scenario, this would involve investigating the Vector Store service health and restoring connectivity.
- [PREVENTIVE_MEASURE]: Implement circuit breakers for the RAG retrieval tool to provide fallback answers when the vector store is down. Add proactive monitoring and alerts for Vector Store connection timeouts.

---

## 5. Individual Contributions & Evidence

### Alice
- [TASKS_COMPLETED]: Implemented CorrelationIdMiddleware for cross-component tracing, configured structlog with JSONL file output, and developed PII scrubbing regex patterns and processor.
- [EVIDENCE_LINK]: [app/middleware.py](file:///d:/AI%20In%20Action/Lab13-Observability/app/middleware.py), [app/logging_config.py](file:///d:/AI%20In%20Action/Lab13-Observability/app/logging_config.py)

### Bob
- [TASKS_COMPLETED]: Integrated Langfuse SDK with @observe decorators for automated tracing, and implemented log enrichment with session and user metadata context.
- [EVIDENCE_LINK]: [app/tracing.py](file:///d:/AI%20In%20Action/Lab13-Observability/app/tracing.py), [app/agent.py](file:///d:/AI%20In%20Action/Lab13-Observability/app/agent.py)

### Charlie
- [TASKS_COMPLETED]: Defined Service Level Objectives (SLOs) in YAML format, configured alert rules for latency and error rates, and authored actionable runbooks in alerts.md.
- [EVIDENCE_LINK]: [config/slo.yaml](file:///d:/AI%20In%20Action/Lab13-Observability/config/slo.yaml), [docs/alerts.md](file:///d:/AI%20In%20Action/Lab13-Observability/docs/alerts.md)

### David
- [TASKS_COMPLETED]: Developed the 6-panel observability dashboard specification and verified real-time metrics capture during load testing.
- [EVIDENCE_LINK]: [docs/dashboard-spec.md](file:///d:/AI%20In%20Action/Lab13-Observability/docs/dashboard-spec.md), [scripts/load_test.py](file:///d:/AI%20In%20Action/Lab13-Observability/scripts/load_test.py)

### Eve
- [TASKS_COMPLETED]: Led the incident response phase by simulating failures, identifying root causes using log/trace analysis, and finalizing the project documentation.
- [EVIDENCE_LINK]: [docs/blueprint-template.md](file:///d:/AI%20In%20Action/Lab13-Observability/docs/blueprint-template.md)

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
