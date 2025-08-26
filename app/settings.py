from pydantic_settings import BaseSettings, Field


class Settings(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(..., env="OPENAI_MODEL")