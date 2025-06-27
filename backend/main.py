import os
import json
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # CORS 미들웨어 임포트
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain.schema.runnable import Runnable
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
#from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import DuckDuckGoSearchRun

# --- 1. FastAPI 애플리케이션 및 데이터 모델 정의 ---

app = FastAPI(
    title="Maritime Exam RAG & Feedback API",
    description="해기사 시험 문제 풀이를 위한 RAG 및 AI 피드백 API 서비스",
    version="1.1.0",
)

# CORS 설정 (매우 중요!)
# 프론트엔드(예: localhost:3000)에서 백엔드(localhost:8000)로 API 요청을 보낼 수 있도록 허용합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # 개발 중에는 모든 출처를 허용. 실제 배포 시에는 프론트엔드 주소로 변경 (예: "http://your-frontend.com")
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)


# Pydantic 모델 정의
class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str


# --- 피드백 요청을 위한 Pydantic 모델 (새로 추가) ---
class FeedbackRequest(BaseModel):
    question: str
    user_answer: str
    correct_answer: str
    is_correct: bool


# --- 피드백 응답을 위한 Pydantic 모델 (새로 추가) ---
class FeedbackResponse(BaseModel):
    result: str
    explanation: str
    tip: str
    relatedConcepts: list[str]


# --- 2. RAG 체인 및 LLM 로드를 위한 설정 ---
rag_chain: Runnable = None
llm: ChatGoogleGenerativeAI = None  # LLM을 전역 변수로 분리


@app.on_event("startup")
async def startup_event():
    global rag_chain, llm
    print("--- 서버 시작: RAG 체인 및 LLM을 로드합니다. ---")
    load_dotenv()
    # ... (기존 RAG 체인 로딩 로직은 동일)

    # LLM 인스턴스 생성
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", temperature=0.3
    )  # 피드백 생성을 위해 약간의 창의성 부여

    # ... (기존 RAG 체인 구성 로직)
    # 1. 로컬 문서 준비
    loader = TextLoader("klm_rules.txt", encoding="utf-8")
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    # 2. 벡터 DB 및 웹 검색 도구 생성
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = Chroma.from_documents(texts, embeddings_model)
    local_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    #web_search_tool = TavilySearchResults(k=3)
    web_search_tool = DuckDuckGoSearchRun()
    # 3. 프롬프트 및 LLM 설정
    template = """
    당신은 AI 어시스턴트입니다.
    주어진 질문에 답변하기 위해 아래에 제공된 '로컬 DB 검색 결과'와 '웹 검색 결과'를 모두 참고하세요.
    두 정보를 종합하여 가장 정확하고 완전한 답변을 생성해주세요.
    만약 정보가 없다면, 정보가 없다고 솔직하게 답변하세요.

    [로컬 DB 검색 결과]
    {context_from_db}

    [웹 검색 결과]
    {context_from_web}

    [질문]
    {question}

    답변:
    """
    prompt = PromptTemplate.from_template(template)

    # 4. RAG 체인 구성
    rag_chain = (
        {
            "context_from_db": local_retriever,
            "context_from_web": web_search_tool,
            "question": lambda x: x["question"],
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    print("--- RAG 체인 및 LLM 로드 완료 ---")


# --- 3. API 엔드포인트 정의 ---


@app.post("/ask", response_model=AnswerResponse, summary="일반 RAG 질의응답")
async def ask_question(request: QuestionRequest):
    # ... (기존 /ask 엔드포인트 로직은 동일)
    if not rag_chain:
        raise HTTPException(status_code=500, detail="RAG 체인이 초기화되지 않았습니다.")
    try:
        answer = rag_chain.invoke({"question": request.question})
        return AnswerResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"답변 생성 중 오류 발생: {e}")


# --- AI 피드백 생성을 위한 엔드포인트 (최종 수정본) ---
@app.post("/feedback", response_model=FeedbackResponse, summary="문제 풀이 AI 피드백 생성")
async def generate_feedback(request: FeedbackRequest):
    """
    사용자의 문제 풀이 결과에 대한 상세한 AI 피드백을 생성합니다.
    """
    if not llm:
        raise HTTPException(status_code=500, detail="LLM이 초기화되지 않았습니다.")

    # 1. 디버깅 로그: 수신된 요청 데이터 확인
    print("\n" + "="*50)
    print(">>> /feedback 엔드포인트 호출됨 <<<")
    print(f"--- 수신된 요청 데이터 ---\n{request.dict()}")

    # 2. LLM에 전달할 프롬프트 구성
    prompt_template = """
    해기사 시험 문제에 대한 상세한 피드백을 한국어로 제공해주세요. 당신은 친절하고 유능한 해기사 시험 튜터입니다.

    - 문제: {question}
    - 사용자가 선택한 답: {user_answer}
    - 정답: {correct_answer}
    - 정답 여부: {is_correct_text}

    아래의 JSON 형식에 맞춰서, 다른 설명이나 불필요한 텍스트 없이 JSON 객체만 반환해주세요.
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
    
    try:
        # 3. LLM 호출 및 결과 추출 (AttributeError 수정 완료)
        print("\n--- LLM에 프롬프트 전송 시작 ---")
        ai_message = llm.invoke(formatted_prompt)
        raw_response = ai_message.content.strip()
        print("--- LLM으로부터 응답 수신 완료 ---")

        # 4. 디버깅 로그: LLM의 원본 응답 출력
        print(f"--- LLM 원본 응답 ---\n{raw_response}\n--------------------")

        # 5. JSON 파싱
        # LLM 응답이 마크다운 코드 블록으로 감싸여 올 경우를 대비
        clean_response = raw_response
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()

        print(f"--- 정리된 응답 (JSON 파싱 대상) ---\n{clean_response}\n---------------------------------")
        feedback_data = json.loads(clean_response)
        print("--- JSON 파싱 성공 ---")
        
        # 6. Pydantic 모델로 변환
        response_model = FeedbackResponse(**feedback_data)
        print("--- Pydantic 모델 변환 성공 ---")
        
        print("="*50 + "\n")
        return response_model
        
    except Exception as e:
        # 7. 강력한 예외 처리 및 전체 트레이스백 출력
        print("\n" + "!"*50)
        print("!!! /feedback 엔드포인트에서 예외 발생 !!!")
        
        # traceback.print_exc()가 전체 오류 스택을 터미널에 출력
        traceback.print_exc() 
        
        print("!"*50 + "\n")
        
        # 클라이언트에게는 일반적인 500 오류를 반환
        raise HTTPException(status_code=500, detail=f"AI 피드백 생성 중 서버 내부 오류 발생")
