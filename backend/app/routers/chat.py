from fastapi import APIRouter, Depends
from app.schemas import ChatRequest, ChatResponse
from app.services.ai_chat import process_chat

from app.auth import RoleChecker

router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"],
    dependencies=[Depends(RoleChecker(["finance_staff", "finance_manager"]))]
)

@router.post("/chat", response_model=ChatResponse)
def chat_with_ai(request: ChatRequest):
    try:
        result = process_chat(request.question, request.department_id, request.fiscal_year)
        return ChatResponse(
            answer=result["answer"],
            source_data=result.get("source_data", [])
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")
