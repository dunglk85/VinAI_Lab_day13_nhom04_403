# Alert Rules and Runbooks

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 3000 for 15m`
- Impact: Tail latency breaches SLO (3000ms)
- First checks:
  1. Open top slow traces in the last 15m
  2. Compare RAG span vs LLM span to identify the bottleneck
  3. Check if incident toggle `rag_slow` is enabled
- Mitigation:
  - Truncate long queries or context
  - Enable fallback retrieval source
  - Reduce prompt/token limit

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 2 for 5m`
- Impact: Users receive failed responses, breaching 2% error SLO
- First checks:
  1. Group logs by `error_type` in the dashboard
  2. Inspect failed traces for specific trace IDs
  3. Check if incident toggle `tool_fail` is active
- Mitigation:
  - Rollback latest deployment if applicable
  - Disable failing tools or features
  - Switch to a more stable fallback model (e.g., GPT-4o-mini to GPT-4o)

## 3. Cost budget spike
- Severity: P3
- Trigger: `hourly_cost_usd > 0.15 for 30m`
- Impact: Burn rate exceeds daily budget of $2.5
- First checks:
  1. Split traces by feature and model to find expensive requests
  2. Compare tokens_in vs tokens_out ratios
  3. Check if `cost_spike` incident was enabled
- Mitigation:
  - Shorten system prompts
  - Route non-critical requests to cheaper models
  - Implement or tune prompt caching

## 4. Low quality score
- Severity: P2
- Trigger: `quality_score_avg < 0.75 for 1h`
- Impact: Output quality is below defined standard
- First checks:
  1. Sample traces with low quality scores (eval scores < 0.5)
  2. Check if prompt templates were recently changed
  3. Identify if specific topics or queries cause the drop
- Mitigation:
  - Revert prompt template changes
  - Update Retrieval parameters (k-value, reranking)
  - Refine system instructions for clarity
