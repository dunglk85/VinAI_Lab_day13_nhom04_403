from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import TypedDict, List

from langgraph.graph import StateGraph, END

from . import metrics
from .mock_llm import FakeLLM
from .mock_rag import retrieve
from .pii import hash_user_id, summarize_text
from .tracing import langfuse_context, observe, get_langfuse_callback, get_langfuse_client


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float


class AgentState(TypedDict):
    question: str
    context: List[str]
    answer: str
    usage: dict
    user_id: str
    session_id: str
    feature: str


class LabAgent:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model
        self.llm = FakeLLM(model=model)
        
        builder = StateGraph(AgentState)
        builder.add_node("retrieve", self._retrieve_node)
        builder.add_node("generate", self._generate_node)
        builder.set_entry_point("retrieve")
        builder.add_edge("retrieve", "generate")
        builder.add_edge("generate", END)
        self.graph = builder.compile()

    @observe(name="node_retrieve")
    def _retrieve_node(self, state: AgentState):
        docs = retrieve(state["question"])
        return {"context": docs}

    @observe(name="node_generate")
    def _generate_node(self, state: AgentState):
        prompt = f"Feature={state['feature']}\nDocs={state['context']}\nQuestion={state['question']}"
        response = self.llm.generate(prompt)
        return {
            "answer": response.text,
            "usage": {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens
            }
        }

    @observe(name="agent_run")
    def run(self, user_id: str, feature: str, session_id: str, message: str) -> AgentResult:
        started = time.perf_counter()
        
        # Cập nhật metadata và Environment
        langfuse_context.update_current_trace(
            user_id=hash_user_id(user_id),
            session_id=session_id,
            tags=["lab", "langgraph", feature, self.model],
        )

        initial_state = {
            "question": message,
            "user_id": user_id,
            "session_id": session_id,
            "feature": feature,
            "context": [],
            "answer": "",
            "usage": {}
        }
        
        callbacks = []
        lf_callback = get_langfuse_callback()
        if lf_callback:
            callbacks.append(lf_callback)

        # Thực thi Graph
        final_state = self.graph.invoke(initial_state, {"callbacks": callbacks})
        
        # Lấy client chính để thực hiện Flush dữ liệu
        client = get_langfuse_client()
        if client:
            try:
                client.flush()
            except Exception:
                pass

        latency_ms = int((time.perf_counter() - started) * 1000)
        tokens_in = final_state["usage"]["input"]
        tokens_out = final_state["usage"]["output"]
        cost_usd = self._estimate_cost(tokens_in, tokens_out)
        quality_score = self._heuristic_quality(message, final_state["answer"], final_state["context"])

        metrics.record_request(
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            quality_score=quality_score,
        )

        return AgentResult(
            answer=final_state["answer"],
            latency_ms=latency_ms,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd,
            quality_score=quality_score,
        )

    def _estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        input_cost = (tokens_in / 1_000_000) * 3
        output_cost = (tokens_out / 1_000_000) * 15
        return round(input_cost + output_cost, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        score = 0.5
        if docs:
            score += 0.2
        if len(answer) > 40:
            score += 0.1
        if question.lower().split()[0:1] and any(token in answer.lower() for token in question.lower().split()[:3]):
            score += 0.1
        if "[REDACTED" in answer:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 2)
