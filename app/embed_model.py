from llama_index.embeddings.openai import OpenAIEmbedding

from .config import settings

def get_embed_model() -> OpenAIEmbedding:
    return OpenAIEmbedding(
        api_key=settings.openai_api_key,
        model=settings.openai_embed_model,
    )