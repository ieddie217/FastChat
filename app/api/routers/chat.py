from fastapi import APIRouter, Depends, Request
import logging
from ...core.auth import get_current_user
from ...schemas.chat import ChatRequest, ChatResponse
from ...core.config import settings
from ...services.openai_client import oai_client

router = APIRouter(prefix="/chat", tags=["chat"])
audit_log = logging.getLogger("audit")

def chat_preview(text: str, max_len: int = 200) -> str:
    if not text:
        return ""
    s = text.replace("\n", " ")
    return (s[:max_len] + "…") if len(s) > max_len else s

@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request, user=Depends(get_current_user)):
    # Call Azure OpenAI
    resp = await oai_client.chat.completions.create(
        model=settings.DEPLOYMENT,
        messages=[m.model_dump() for m in req.messages],
        temperature=0.2,
    )
    msg = resp.choices[0].message.content
    usage = getattr(resp, "usage", None)

    out = ChatResponse(
        reply=msg,
        source="model",
        usage_prompt_tokens=getattr(usage, "prompt_tokens", None) if usage else None,
        usage_completion_tokens=getattr(usage, "completion_tokens", None) if usage else None,
        usage_total_tokens=getattr(usage, "total_tokens", None) if usage else None,
    )

    # ---- Optional AUDIT LOG (only if DEBUG_AUDIT=true and handler attached) ----
    if settings.DEBUG_AUDIT and audit_log.handlers:
        # Last user message as the "question"
        question = ""
        for m in reversed(req.messages):
            if m.role == "user":
                question = m.content or ""
                break

        # Request ID from middleware
        req_id = getattr(request.state, "request_id", None)

        audit_log.info(
            "chat_audit",
            extra={
                "req_id": req_id,
                "user": user.get("username"),
                "model": settings.DEPLOYMENT,
                "tokens_prompt": out.usage_prompt_tokens,
                "tokens_completion": out.usage_completion_tokens,
                "tokens_total": out.usage_total_tokens,
                "question_preview": chat_preview(question, 200),
                # leave access-only fields null to keep audit narrow
                "client_ip": None,
                "method": None,
                "path": "/chat",
                "status": None,
                "elapsed_ms": None,
                "user_agent": None,
            },
        )

    return out
