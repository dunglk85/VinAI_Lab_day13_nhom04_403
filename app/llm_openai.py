from __future__ import annotations

import os
from typing import Any

import openai
from .llm_interface import BaseLLM, LLMResponse, LLMUsage
from .tracing import observe


class OpenAILLM(BaseLLM):
    def __init__(self, model: str = "gpt-4o") -> None:
        super().__init__(model=model)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        self.client = openai.OpenAI(api_key=api_key)

    @observe(as_type="generation")
    def generate(self, prompt: str) -> LLMResponse:
        """
        Generate a response using OpenAI's Chat Completion API.
        """
        # If API key is missing, this will raise an error if not in mock mode.
        # For the sake of this lab, we assume the environment is configured.
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        return LLMResponse(
            text=response.choices[0].message.content or "",
            usage=LLMUsage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens
            ),
            model=self.model,
            raw_response=response
        )
