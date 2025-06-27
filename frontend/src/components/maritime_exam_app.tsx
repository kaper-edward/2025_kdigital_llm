import React, { useState } from 'react';
import { ChevronRight, ArrowLeft, Calendar, Settings, CheckCircle, XCircle, Brain, X } from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:8000';

const MaritimeExamApp = () => {
  const [currentScreen, setCurrentScreen] = useState('main');
  const [selectedExamType, setSelectedExamType] = useState('');
  const [selectedGrade, setSelectedGrade] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [selectedExam, setSelectedExam] = useState('');
  const [selectedSubjects, setSelectedSubjects] = useState([
    'navigation', 'operation', 'law', 'cargo', 'fishing'
  ]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [examMode, setExamMode] = useState('practice'); // 'practice' or 'real'
  const [aiFeedback, setAiFeedback] = useState('');
  const [isLoadingFeedback, setIsLoadingFeedback] = useState(false);

  // 샘플 문제 데이터
  const sampleQuestions = [
    {
      id: 1,
      subject: '항해',
      question: '좋이해도 위에 편차가 기재되어 있는 부분은?',
      options: [
        { key: 'A', text: '해류도' },
        { key: 'B', text: '방위환' },
        { key: 'C', text: '나침도' },
        { key: 'D', text: '지방자기' }
      ],
      correctAnswer: 'C',
      explanation: '나침도(Compass Rose)는 해도에서 자북과 진북의 편차, 자차 등의 정보가 기재되는 부분입니다.'
    },
    {
      id: 2,
      subject: '항해',
      question: '선박의 안전항행을 위한 국제규칙은?',
      options: [
        { key: 'A', text: 'COLREG' },
        { key: 'B', text: 'SOLAS' },
        { key: 'C', text: 'MARPOL' },
        { key: 'D', text: 'STCW' }
      ],
      correctAnswer: 'A',
      explanation: 'COLREG(국제해상충돌예방규칙)은 선박의 안전항행을 위한 국제규칙입니다.'
    },
    {
      id: 3,
      subject: '운용',
      question: '선박의 복원성을 나타내는 요소는?',
      options: [
        { key: 'A', text: 'GM' },
        { key: 'B', text: 'DWT' },
        { key: 'C', text: 'LOA' },
        { key: 'D', text: 'GRT' }
      ],
      correctAnswer: 'A',
      explanation: 'GM(Metacentric Height)은 선박의 복원성을 나타내는 중요한 요소입니다.'
    }
  ];

  const examTypes = [
    { id: 'navigator', name: '항해사', icon: '🧭' },
    { id: 'engineer', name: '기관사', icon: '⚙️' },
    { id: 'small_craft', name: '소형선박조종사', icon: '🚤' }
  ];

  const grades = [
    { id: '1', name: '항해사 1급' },
    { id: '2', name: '항해사 2급' },
    { id: '3', name: '항해사 3급' },
    { id: '4', name: '항해사 4급' },
    { id: '5', name: '항해사 5급' },
    { id: '6', name: '항해사 6급' },
    { id: '6_domestic', name: '항해사 6급 (국내한정 상선)' }
  ];

  const allSubjects = [
    { id: 'navigation', name: '항해' },
    { id: 'operation', name: '운용' },
    { id: 'law', name: '법규' },
    { id: 'cargo', name: '상선전문' },
    { id: 'fishing', name: '어선전문' }
  ];

  const years = [
    { id: '2022', name: '2022년 시행' },
    { id: '2023', name: '2023년 시행' }
  ];

  const exams = [
    { id: '1', name: '1회 기출문제', status: 'available' },
    { id: '2', name: '2회 기출문제', status: 'download' },
    { id: '3', name: '3회 기출문제', status: 'download' },
    { id: '4', name: '4회 기출문제', status: 'download' }
  ];

  const toggleSubject = (subjectId) => {
    setSelectedSubjects(prev => 
      prev.includes(subjectId)
        ? prev.filter(id => id !== subjectId)
        : [...prev, subjectId]
    );
  };

  const generateAIFeedback = async (question, userAnswer, correctAnswer, isCorrect) => {
    setIsLoadingFeedback(true);
    setAiFeedback(''); // 이전 피드백 초기화

    try {
      // 백엔드에 보낼 요청 본문 데이터
      const requestBody = {
        question: question,
        user_answer: userAnswer,
        correct_answer: correctAnswer,
        is_correct: isCorrect
      };

      // 백엔드의 /feedback 엔드포인트에 POST 요청 보내기
      const response = await fetch(`${API_BASE_URL}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        // 서버에서 4xx, 5xx 에러 응답을 보냈을 경우
        throw new Error(`API 요청 실패: ${response.statusText}`);
      }

      // 백엔드로부터 받은 JSON 응답을 파싱
      const feedbackData = await response.json();
      
      // 상태 업데이트
      setAiFeedback(feedbackData);

    } catch (error) {
      console.error('AI 피드백 생성 오류:', error);
      // 백엔드 호출 실패 시 보여줄 기본 폴백(fallback) 피드백
      setAiFeedback({
        result: isCorrect ? '정답' : '오답',
        explanation: 'AI 피드백을 가져오는 데 실패했습니다. 기본 해설입니다: 이 문제의 정답은 ' + correctAnswer + '입니다.',
        tip: '네트워크 연결을 확인하거나 잠시 후 다시 시도해주세요.',
        relatedConcepts: []
      });
    } finally {
      setIsLoadingFeedback(false);
    }
  };

  const handleAnswerSelect = async (answer) => {
    setSelectedAnswer(answer);
    
    // 즉시 결과 표시
    const currentQuestion = sampleQuestions[currentQuestionIndex];
    const isCorrect = answer === currentQuestion.correctAnswer;
    
    // AI 피드백 생성
    await generateAIFeedback(
      currentQuestion.question,
      answer,
      currentQuestion.correctAnswer,
      isCorrect
    );
    
    setShowResult(true);
  };

  const closeResult = () => {
    setShowResult(false);
    setAiFeedback('');
    setSelectedAnswer('');
  };

  const handleNextQuestion = () => {
    closeResult();
    if (currentQuestionIndex < sampleQuestions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      // 시험 완료
      alert('시험이 완료되었습니다!');
      setCurrentScreen('main');
      setCurrentQuestionIndex(0);
    }
  };

  const handlePrevQuestion = () => {
    closeResult();
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const goBack = () => {
    if (currentScreen === 'question') {
      setCurrentScreen('exams');
    } else if (currentScreen === 'exams') {
      setCurrentScreen('years');
    } else if (currentScreen === 'years') {
      setCurrentScreen('grades');
    } else if (currentScreen === 'grades') {
      setCurrentScreen('main');
    }
  };

  const renderMainScreen = () => (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white p-6 text-center">
        <div className="flex justify-center mb-4">
          <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white text-2xl">🧭</span>
          </div>
        </div>
        <h1 className="text-2xl font-bold text-blue-600 mb-2">어떤 시험을 준비하세요?</h1>
      </div>

      {/* Exam Type Selection */}
      <div className="flex-1 p-4">
        {examTypes.map((type) => (
          <button
            key={type.id}
            onClick={() => {
              setSelectedExamType(type.id);
              setCurrentScreen('grades');
            }}
            className="w-full bg-white rounded-lg p-4 mb-3 flex items-center justify-between shadow-sm border hover:bg-gray-50"
          >
            <span className="text-lg font-medium">{type.name}</span>
            <ChevronRight className="w-5 h-5 text-gray-400" />
          </button>
        ))}
      </div>

      {/* Bottom Navigation */}
      <div className="bg-white p-4 flex justify-around border-t">
        <button className="flex flex-col items-center text-blue-500">
          <Calendar className="w-6 h-6 mb-1" />
          <span className="text-xs">시험정보</span>
        </button>
        <button className="flex flex-col items-center text-gray-400">
          <Settings className="w-6 h-6 mb-1" />
          <span className="text-xs">환경설정</span>
        </button>
      </div>
    </div>
  );

  const renderGradesScreen = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white p-4 flex items-center border-b">
        <button onClick={goBack} className="mr-4">
          <ArrowLeft className="w-6 h-6" />
        </button>
        <div className="flex items-center text-blue-500">
          <span className="text-sm">📋 항해사</span>
          <ChevronRight className="w-4 h-4 mx-1" />
        </div>
      </div>

      {/* Grades List */}
      <div className="p-4">
        {grades.map((grade) => (
          <button
            key={grade.id}
            onClick={() => {
              setSelectedGrade(grade.id);
              setCurrentScreen('years');
            }}
            className="w-full bg-white rounded-lg p-4 mb-3 flex items-center justify-between shadow-sm"
          >
            <span className="text-lg">{grade.name}</span>
            <ChevronRight className="w-5 h-5 text-gray-400" />
          </button>
        ))}
      </div>
    </div>
  );

  const renderYearsScreen = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white p-4 flex items-center border-b">
        <button onClick={goBack} className="mr-4">
          <ArrowLeft className="w-6 h-6" />
        </button>
        <div className="flex items-center text-blue-500">
          <span className="text-sm">📋 항해사</span>
          <ChevronRight className="w-4 h-4 mx-1" />
          <span className="text-sm">6급</span>
          <ChevronRight className="w-4 h-4 mx-1" />
        </div>
      </div>

      {/* Years List */}
      <div className="p-4">
        {years.map((year) => (
          <button
            key={year.id}
            onClick={() => {
              setSelectedYear(year.id);
              setCurrentScreen('exams');
            }}
            className="w-full bg-white rounded-lg p-4 mb-3 flex items-center justify-between shadow-sm"
          >
            <div className="flex items-center">
              <Calendar className="w-5 h-5 text-blue-500 mr-3" />
              <span className="text-lg">{year.name}</span>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400" />
          </button>
        ))}
      </div>
    </div>
  );

  const renderExamsScreen = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white p-4 flex items-center border-b">
        <button onClick={goBack} className="mr-4">
          <ArrowLeft className="w-6 h-6" />
        </button>
        <div className="flex items-center text-blue-500 text-sm">
          <span>📋 항해사</span>
          <ChevronRight className="w-4 h-4 mx-1" />
          <span>6급</span>
          <ChevronRight className="w-4 h-4 mx-1" />
          <span>2023년도 1회 기출문제</span>
          <ChevronRight className="w-4 h-4 mx-1" />
        </div>
      </div>

      {/* Exam Selection */}
      <div className="p-4">
        <div className="bg-white rounded-lg p-4 mb-4">
          <h3 className="text-lg font-bold mb-4">1회 기출문제</h3>
          
          <div className="mb-4">
            <h4 className="text-sm font-medium mb-2">과목 선택</h4>
            <div className="grid grid-cols-2 gap-2">
              {allSubjects.map((subject) => (
                <button
                  key={subject.id}
                  onClick={() => toggleSubject(subject.id)}
                  className={`p-2 rounded-full text-sm border-2 transition-colors ${
                    selectedSubjects.includes(subject.id)
                      ? 'bg-orange-500 text-white border-orange-500' 
                      : 'bg-white text-gray-600 border-gray-300'
                  }`}
                >
                  {selectedSubjects.includes(subject.id) ? '✓' : '○'} {subject.name}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-2">
            <button 
              onClick={() => setExamMode('practice')}
              className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
                examMode === 'practice' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              실전모드
            </button>
            <button 
              onClick={() => setExamMode('real')}
              className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
                examMode === 'real' 
                  ? 'bg-orange-500 text-white' 
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              연습모드
            </button>
          </div>
        </div>

        <button 
          onClick={() => {
            if (selectedSubjects.length === 0) {
              alert('최소 하나의 과목을 선택해주세요.');
              return;
            }
            setCurrentScreen('question');
            setCurrentQuestionIndex(0);
          }}
          className="w-full bg-orange-500 text-white py-4 rounded-lg font-medium text-lg hover:bg-orange-600 transition-colors"
        >
          시험 시작하기
        </button>
      </div>
    </div>
  );

  const renderQuestionScreen = () => {
    const currentQuestion = sampleQuestions[currentQuestionIndex];
    
    return (
      <div className="min-h-screen bg-gray-50 relative">
        {/* Header */}
        <div className="bg-white p-4 flex items-center border-b">
          <button onClick={goBack} className="mr-4">
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div className="flex items-center text-blue-500 text-sm">
            <span>📋 항해사</span>
            <ChevronRight className="w-4 h-4 mx-1" />
            <span>6급</span>
            <ChevronRight className="w-4 h-4 mx-1" />
            <span>2023년도 1회 기출문제</span>
            <ChevronRight className="w-4 h-4 mx-1" />
          </div>
        </div>

        {/* Question */}
        <div className="p-6 pb-24">
          <div className="bg-white rounded-lg p-6 mb-6">
            <div className="text-blue-600 font-medium mb-4">
              {currentQuestionIndex + 1}.{currentQuestion.subject} {currentQuestionIndex + 1}/{sampleQuestions.length}
            </div>
            <h2 className="text-lg font-medium mb-6">{currentQuestion.question}</h2>
            
            <div className="space-y-3">
              {currentQuestion.options.map((option) => (
                <button
                  key={option.key}
                  onClick={() => handleAnswerSelect(option.key)}
                  disabled={showResult}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-colors ${
                    selectedAnswer === option.key
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  } ${showResult ? 'cursor-not-allowed opacity-60' : ''}`}
                >
                  <span className="font-medium">{option.key}.</span> {option.text}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Result Overlay */}
        {showResult && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[80vh] overflow-y-auto">
              {isLoadingFeedback ? (
                <div className="text-center">
                  <Brain className="w-12 h-12 text-blue-500 mx-auto mb-4 animate-pulse" />
                  <p className="text-lg font-medium">AI가 피드백을 생성중...</p>
                </div>
              ) : (
                <>
                  <div className="flex justify-between items-start mb-4">
                    <div className="text-center flex-1">
                      {aiFeedback?.result === '정답' ? (
                        <>
                          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                          <h3 className="text-2xl font-bold text-green-600 mb-2">정답이에요</h3>
                        </>
                      ) : (
                        <>
                          <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                          <h3 className="text-2xl font-bold text-red-600 mb-2">틀렸어요</h3>
                        </>
                      )}
                    </div>
                    <button
                      onClick={closeResult}
                      className="text-gray-400 hover:text-gray-600 p-1"
                    >
                      <X className="w-6 h-6" />
                    </button>
                  </div>

                  {aiFeedback && (
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-gray-800 mb-2">🤖 AI 상세 설명</h4>
                        <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                          {aiFeedback.explanation}
                        </p>
                      </div>
                      
                      {aiFeedback.tip && (
                        <div>
                          <h4 className="font-medium text-gray-800 mb-2">💡 학습 팁</h4>
                          <p className="text-sm text-blue-600 bg-blue-50 p-3 rounded-lg">
                            {aiFeedback.tip}
                          </p>
                        </div>
                      )}

                      {aiFeedback.relatedConcepts && aiFeedback.relatedConcepts.length > 0 && (
                        <div>
                          <h4 className="font-medium text-gray-800 mb-2">📚 관련 개념</h4>
                          <div className="flex flex-wrap gap-2">
                            {aiFeedback.relatedConcepts.map((concept, index) => (
                              <span 
                                key={index}
                                className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full"
                              >
                                {concept}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="flex gap-2 mt-6">
                    <button
                      onClick={closeResult}
                      className="flex-1 py-3 bg-gray-200 text-gray-600 rounded-lg font-medium"
                    >
                      닫기
                    </button>
                    <button
                      onClick={handleNextQuestion}
                      className="flex-1 py-3 bg-orange-500 text-white rounded-lg font-medium"
                    >
                      다음 문제
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* Bottom Navigation */}
        <div className="fixed bottom-0 left-0 right-0 bg-white p-4 border-t">
          <div className="flex gap-3">
            <button 
              onClick={handlePrevQuestion}
              disabled={currentQuestionIndex === 0}
              className="flex-1 py-3 bg-gray-200 text-gray-600 rounded-lg disabled:opacity-50"
            >
              이전
            </button>
            <button 
              onClick={handleNextQuestion}
              disabled={currentQuestionIndex === sampleQuestions.length - 1}
              className="flex-1 py-3 bg-gray-200 text-gray-600 rounded-lg disabled:opacity-50"
            >
              다음
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Screen Routing
  switch (currentScreen) {
    case 'main':
      return renderMainScreen();
    case 'grades':
      return renderGradesScreen();
    case 'years':
      return renderYearsScreen();
    case 'exams':
      return renderExamsScreen();
    case 'question':
      return renderQuestionScreen();
    default:
      return renderMainScreen();
  }
};

export default MaritimeExamApp;