import os
import json
import pymysql
import re

# --- 1. 설정 및 상수 정의 ---
# 'exam' 폴더가 있는 상위 경로를 지정하세요.
# 예: C:/Users/tykim/dev/llm/utils
BASE_DATA_PATH = '.' # 현재 스크립트 위치를 기준으로 탐색
ROOT_EXAM_DIR = os.path.join(BASE_DATA_PATH, "exam")

# 데이터베이스 연결 정보 (본인 환경에 맞게 수정)
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "1111", # 실제 비밀번호 입력
    "db": "maritime_exam",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

def read_json_with_fallback(path):
    """
    파일을 UTF-8로 먼저 읽고, 실패 시 CP949로 다시 읽어 JSON 객체를 반환합니다.
    """
    try:
        # 1순위: UTF-8으로 시도
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except UnicodeDecodeError:
        try:
            # 2순위: CP949로 시도
            with open(path, 'r', encoding='cp949') as f:
                print(f"  - 인코딩 정보: '{path}' 파일이 CP949로 처리되었습니다.")
                return json.load(f)
        except Exception as e:
            print(f"❌ 파일 읽기 실패 (CP949): {path} | 오류: {e}")
            return None
    except Exception as e:
        print(f"❌ 파일 읽기 실패 (UTF-8): {path} | 오류: {e}")
        return None


def get_exam_details_from_path(path):
    """경로 문자열에서 시험 정보를 추출합니다."""
    try:
        parts = path.split(os.sep)
        license_type = parts[-2]
        dir_name = os.path.basename(path)
        
        # 정규표현식을 사용하여 폴더 이름에서 정보 추출
        match = re.match(r'([A-Z])(\d+)_(\d{4})_(\d{2})', dir_name)
        if not match:
            return None, None, None, None

        _, grade_num, year, inning = match.groups()
        grade = f"{grade_num}급"
        
        return license_type, grade, int(year), int(inning)
    except IndexError:
        return None, None, None, None


# --- 2. 데이터 임포트 메인 로직 ---
try:
    # 데이터베이스 연결
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("✅ 데이터베이스 연결 성공")

    # 트랜잭션 시작
    conn.begin()

    # exam 폴더 하위의 모든 json 파일 탐색
    for dirpath, _, filenames in os.walk(ROOT_EXAM_DIR):
        for filename in filenames:
            if filename.endswith('.json'):
                json_path = os.path.join(dirpath, filename)

                try:
                    license_type, grade, year, inning = get_exam_details_from_path(dirpath)
                    if not all([license_type, grade, year, inning]):
                        print(f"⚠️ 건너뜀 (경로에서 시험 정보 추출 실패): {dirpath}")
                        continue
                    
                    exam_data = read_json_with_fallback(json_path)
                    if exam_data is None:
                        continue # 파일 읽기 실패 시 다음 파일로 넘어감

                    sql_exam = """
                        INSERT INTO exams (license_type, grade, year, inning)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id);
                    """
                    cursor.execute(sql_exam, (license_type, grade, year, inning))
                    exam_id = cursor.lastrowid
                    print(f"\n-> 처리 시작: {license_type} {grade} ({year}년 {inning}회), Exam_ID: {exam_id}")

                    subject_info = exam_data.get("subject", {})
                    if not subject_info or "type" not in subject_info:
                        print(f"  - 경고: '{filename}' 파일에 'subject' 또는 'type' 키가 없습니다.")
                        continue

                    for subject in subject_info.get("type", []):
                        subject_name = subject.get("string")
                        if not subject_name: continue

                        sql_subject = "INSERT INTO subjects (exam_id, name) VALUES (%s, %s)"
                        cursor.execute(sql_subject, (exam_id, subject_name))
                        subject_id = cursor.lastrowid
                        
                        question_count = 0
                        questions = subject.get("questions", [])
                        if not questions: continue

                        for question in questions:
                            answer_map = {'가': 'a', '나': 'b', '다': 'c', '라': 'd', '사': 'd', '아': 'a'} # '사'는 라, '아'는 가로 매핑하는 등 예외처리
                            correct_answer_key = answer_map.get(str(question.get("answer")), "unknown")
                            
                            image_ref = next((str(val) for val in question.values() if isinstance(val, str) and val.startswith('@')), None)

                            sql_question = """
                                INSERT INTO questions (subject_id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer, image_ref)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            params = (
                                subject_id, question.get("num"), question.get("questionsStr"),
                                question.get("ex1Str"), question.get("ex2Str"), question.get("ex3Str"),
                                question.get("ex4Str"), correct_answer_key, image_ref
                            )
                            cursor.execute(sql_question, params)
                            question_count += 1
                        
                        print(f"  -> '{subject_name}' 과목의 문제 {question_count}개 처리 완료.")

                except Exception as e:
                    print(f"❌ 파일 처리 중 예기치 않은 오류 발생: {json_path} | {e}")

    conn.commit()
    print("\n✅ 모든 기출문제 데이터가 성공적으로 임포트되었습니다.")

except pymysql.Error as e:
    if 'conn' in locals() and conn.open:
        conn.rollback()
    print(f"❌ 데이터베이스 작업 중 오류 발생: {e}")

finally:
    if 'conn' in locals() and conn.open:
        conn.close()
        print("🔌 데이터베이스 연결이 종료되었습니다.")