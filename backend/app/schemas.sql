-- 데이터베이스가 없다면 생성
CREATE DATABASE IF NOT EXISTS maritime_exam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE maritime_exam;

-- 기존 테이블이 있다면 삭제 (초기화용)
DROP TABLE IF EXISTS `questions`;
DROP TABLE IF EXISTS `subjects`;
DROP TABLE IF EXISTS `exams`;

-- ---------------------------------
-- 1. 시험 정보 테이블 (exams) - 수정됨
-- ---------------------------------
CREATE TABLE `exams` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `license_type` VARCHAR(50) NOT NULL COMMENT '자격증 종류 (기관사, 항해사, 소형선박조종사)',
  `grade` VARCHAR(100) NOT NULL COMMENT '상세 급수 (예: 1급, 6급, 6급 (국내한정 상선))',
  `year` INT NOT NULL COMMENT '시행 연도',
  `inning` INT NOT NULL COMMENT '회차',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_exam_instance` (`license_type`, `grade`, `year`, `inning`) COMMENT '시험의 유일성 보장'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='시험 정보';

-- ---------------------------------
-- 2. 과목 정보 테이블 (subjects) - 변경 없음
-- ---------------------------------
CREATE TABLE `subjects` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `exam_id` INT NOT NULL COMMENT 'exams 테이블 외래키',
  `name` VARCHAR(100) NOT NULL COMMENT '과목명 (예: 1.항해)',
  PRIMARY KEY (`id`),
  KEY `fk_subjects_exam_id` (`exam_id`),
  CONSTRAINT `fk_subjects_exam_id` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='과목 정보';

-- ---------------------------------
-- 3. 문제 정보 테이블 (questions) - 변경 없음
-- ---------------------------------
CREATE TABLE `questions` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `subject_id` INT NOT NULL COMMENT 'subjects 테이블 외래키',
  `question_number` INT NOT NULL COMMENT '문제 번호',
  `question_text` TEXT NOT NULL COMMENT '질문 내용',
  `option_a` TEXT NOT NULL COMMENT '보기 1 (가)',
  `option_b` TEXT NOT NULL COMMENT '보기 2 (나)',
  `option_c` TEXT NOT NULL COMMENT '보기 3 (다)',
  `option_d` TEXT NOT NULL COMMENT '보기 4 (라)',
  `correct_answer` VARCHAR(10) NOT NULL COMMENT '정답 키 (a,b,c,d)',
  `image_ref` VARCHAR(255) DEFAULT NULL COMMENT '이미지 참조 (예: @pic1106_a)',
  PRIMARY KEY (`id`),
  KEY `fk_questions_subject_id` (`subject_id`),
  CONSTRAINT `fk_questions_subject_id` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='문제 정보';