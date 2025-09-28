from llama_index.llms.openai import OpenAI

from .config import settings

def get_llm() -> OpenAI:
    return OpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_llm,
    )