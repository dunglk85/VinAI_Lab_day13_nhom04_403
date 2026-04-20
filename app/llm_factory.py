from __future__ import annotations

from .llm_interface import BaseLLM
from .mock_llm import FakeLLM
from .llm_openai import OpenAILLM


def create_llm(model: str) -> BaseLLM:
    """
    Factory function to create the appropriate LLM instance based on model name.
    """
    try:
        if model.startswith("gpt-"):
            return OpenAILLM(model=model)
    except Exception as e:
        # Trong thực tế, bạn nên log lỗi này lại
        print(f"Warning: Failed to initialize {model}, falling back to FakeLLM. Error: {e}")
    
    # Mặc định sử dụng FakeLLM cho các model khác hoặc model mặc định của lab
    return FakeLLM(model=model)
