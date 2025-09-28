from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_embed_model: str
    openai_embed_dim: int
    openai_llm: str

    # LlamaIndex
    storage_dir: str = './storage'
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings() # type: ignore