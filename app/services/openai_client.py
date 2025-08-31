from openai import AsyncAzureOpenAI
from ..core.config import settings

# Create once and reuse
oai_client = AsyncAzureOpenAI(
    api_key=settings.KEY,
    azure_endpoint=settings.ENDPOINT,
    api_version=settings.API_VERSION,
)
