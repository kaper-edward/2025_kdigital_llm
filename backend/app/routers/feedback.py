# /app/routers/feedback.py
from fastapi import APIRouter, HTTPException
from app import schemas
from app.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)

# LLM 인스턴스 초기화
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    google_api_key=settings.GOOGLE_API_KEY
)

@router.post("/", response_model=schemas.FeedbackResponse)
async def generate_feedback(request: schemas.FeedbackRequest):
    """
    사용자의 문제 풀이 결과에 대한 상세한 AI 피드백을 생성합니다.
    """
    prompt_template = """
    당신은 친절하고 유능한 해기사 시험 전문 튜터입니다.
    다음 문제와 사용자의 답변에 대해, 아래 JSON 형식에 맞춰 상세한 피드백을 한국어로 제공해주세요.
    - 문제: {question}
    - 사용자가 선택한 답: {user_answer}
    - 정답: {correct_answer}
    - 정답 여부: {is_correct_text}

    JSON 형식 (다른 설명 없이 JSON 객체만 반환):
    {{
      "result": "{is_correct_text}",
      "explanation": "정답에 대한 매우 상세하고 명확한 설명. 왜 이 답이 정답이고 다른 답은 오답인지 구체적으로 설명해주세요.",
      "tip": "이 문제와 관련된 개념을 효과적으로 학습하고 기억하기 위한 팁이나 암기법을 제시해주세요.",
      "relatedConcepts": ["이 문제와 관련된 주요 개념이나 용어 3가지를 리스트 형태로 제공해주세요."]
    }}
    """
    
    is_correct_text = "정답" if request.is_correct else "오답"
    
    formatted_prompt = prompt_template.format(
        question=request.question,
        user_answer=request.user_answer,
        correct_answer=request.correct_answer,
        is_correct_text=is_correct_text
    )
    
    # --- [수정된 부분] 프롬프트 로그 출력 ---
    print("="*50)
    print(">>> AI 피드백 생성을 위해 아래 프롬프트를 사용합니다:")
    print(formatted_prompt)
    print("="*50)
    # ------------------------------------
    
    try:
        ai_message = llm.invoke(formatted_prompt)
        # LLM 응답이 마크다운 코드 블록으로 감싸여 올 경우 대비
        clean_response = ai_message.content.strip().removeprefix("```json").removesuffix("```").strip()
        
        # FeedbackResponse 모델로 직접 변환하여 반환
        return schemas.FeedbackResponse.parse_raw(clean_response)

    except Exception as e:
        print(f"AI 피드백 생성 오류: {e}")
        raise HTTPException(status_code=500, detail="AI 피드백 생성 중 서버 내부 오류가 발생했습니다.")