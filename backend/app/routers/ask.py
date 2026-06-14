from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import AIAskRequest, AIAskResponse
from app.services.ai_agent import ask_question
from app.database import get_db
from app.models import AIQuery

router = APIRouter(
    prefix="/ai",
    tags=["AI Agent"]
)

@router.post("/ask", response_model=AIAskResponse)
def handle_ai_ask(request: AIAskRequest, db: Session = Depends(get_db)):
    # 1. Call AI Agent
    agent_result = ask_question(request.question, request.fiscal_year or 2026)
    answer_markdown = agent_result["answer_markdown"]
    used_tools = agent_result["used_tools"]
    
    # 2. Save to database
    try:
        new_query = AIQuery(
            question=request.question,
            answer=answer_markdown
        )
        db.add(new_query)
        db.commit()
    except Exception as e:
        print("Failed to save AI query to DB:", e)
        db.rollback()

    # 3. Return response
    return AIAskResponse(
        answer_markdown=answer_markdown,
        used_tools=used_tools
    )
