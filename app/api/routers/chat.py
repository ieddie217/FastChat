from fastapi import APIRouter, Depends
from ...core.auth import get_current_user
from ...schemas.chat import ChatRequest, ChatResponse
from ...core.config import settings
from ...services.openai_client import oai_client

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, user=Depends(get_current_user)):
    resp = await oai_client.chat.completions.create(
        model=settings.DEPLOYMENT,
        messages=[m.model_dump() for m in req.messages],
        temperature=0.2,
    )
    msg = resp.choices[0].message.content
    usage = getattr(resp, "usage", None)
    return ChatResponse(
        reply=msg,
        source="model",
        usage_prompt_tokens=getattr(usage, "prompt_tokens", None) if usage else None,
        usage_completion_tokens=getattr(usage, "completion_tokens", None) if usage else None,
        usage_total_tokens=getattr(usage, "total_tokens", None) if usage else None,
    )
