## 1. 프로젝트 개요

- **목표**: 향수 취향 테스트와 추천 흐름을 중심으로, DB 설계서에 맞는 **Streamlit + Supabase 기반 DB 응용 Skeleton**을 구축한다.
- **핵심 포인트**:
  - `perfume_notes` / `scents` / `scent_categories` 중심의 **관계형 모델을 그대로 활용**
  - 추천 점수 계산을 **가능한 한 SQL로 표현**하고, Python/Streamlit은 UI와 오케스트레이션에 집중
  - 추후 로그인, 저장/비교, AI 확장 등이 **무리 없이 붙을 수 있는 구조** 유지

---

## 2. 프로젝트 구조(Skeleton)

프로젝트 루트:

- `app.py`
  - Streamlit 진입점
  - 공통 레이아웃, 상단 네비게이션, 페이지 라우팅 정도만 담당

- `pages/`
  - `01_preference_test.py`
    - 취향 테스트 진행 화면 (향 계열 → 세부 향 → 발향 시점 → 추가 향 계열)
    - 사용자의 선택을 `services` 계층으로 전달
  - `02_recommendation_result.py`
    - 추천 결과 Top 5 조회/표시
    - (Skeleton 단계) 저장/비교 버튼 UI만 배치 가능, 실제 로직은 이후 단계에서 구현

- `database/`
  - `supabase_client.py`
    - `create_client()` 호출 + `st.secrets["SUPABASE_URL"]`, `st.secrets["SUPABASE_KEY"]` 사용
    - 다른 모듈에서 재사용 가능한 단일 인스턴스 제공
  - `repositories/`
    - `scent_repository.py`
      - `get_scent_categories()`
      - `get_scents_by_category(category_id)`
    - `preference_repository.py`
      - `create_user_preference_test(user_id | None) -> test_id`
      - `save_main_choice(test_id, category_id, scent_id, preferred_note_type)`
      - `save_additional_categories(test_id, category_ids: list[int])`
    - `recommendation_repository.py`
      - `save_recommendation_results(test_id, recommendations: list[dict])`
      - `get_recommendations_by_test(test_id)`

- `services/`
  - `recommendation_service.py`
    - 스트림릿에서 받은 입력(메인 향 계열, 메인 scent, note_type, 추가 계열)을 받아
      - (1) 필요시 `user_preference_tests` 및 관련 선택값 테이블에 저장
      - (2) `sql/recommendation_scoring.sql` 기반 쿼리를 호출하여 Top 5 추천 결과를 얻음
      - (3) `recommendation_results`에 스코어/향수 ID를 저장
    - 반환 값:
      - 추천 향수 리스트(Top 5)
      - 각 추천에 대한 **설명용 메타데이터**(예: 일치한 조건, 분위기 키워드)

- `sql/`
  - `recommendation_scoring.sql`
    - 특정 테스트 입력 값(또는 파라미터)을 기준으로 `perfume_notes`, `scents`, `scent_categories`를 조인
    - 메인 향 / note_type / 추가 category 일치를 기반으로 **점수를 계산하는 SQL 뼈대** 정의
    - Streamlit 코드에서는 이 SQL을 문자열로 로딩해서 `supabase.rpc` 또는 `supabase.table(...).execute()` 등으로 호출

- `utils/`
  - `scent_normalization.py`
    - 한국어 입력(또는 CSV 원본)에서 영어 canonical로 매핑하는 규칙/딕셔너리 정의
    - 예: `"패출리"`, `"파출리"` → `"Patchouli"`

- `docs/`
  - 기존 기획서/DB 설계 문서 유지 (참조용)

- `spec/`
  - 현재 문서(`DB_application_skeleton_spec.md`)
  - 이후 단계에서 UI 플로우, 서비스 레이어 등 추가 스펙 문서 확장 가능

---

## 3. UI 흐름(Skeleton)

### 3.1 비로그인 기준 최소 흐름

1. 사용자가 `app.py` 진입
2. `pages/01_preference_test.py`로 이동
3. Preference Test 단계
   - 1단계: 향 계열 선택 (최대 1개)
   - 2단계: 선택한 향 계열 내 세부 향 선택 (최대 1개, Skeleton은 1개 우선)
   - 3단계: 발향 시점 선택 (`top`, `middle`, `base` 중 1개)
   - 4단계: 추가로 좋아하는 향 계열 (0~2개 복수 선택)
4. “테스트 완료 및 추천 보기” 버튼 클릭 시:
   - (a) `services.recommendation_service`에 입력 전달
   - (b) 내부적으로 `user_preference_tests` / `user_test_main_choice` / `user_test_additional_categories`에 기록
   - (c) 추천 SQL 실행 → 점수/향수 리스트 계산 → `recommendation_results` 저장
   - (d) `st.session_state`에 `test_id` 및 추천 결과 ID/리스트 저장
   - (e) `pages/02_recommendation_result.py`로 전환
5. 결과 페이지에서:
   - Top 5 향수를 카드 형태로 표시
   - 각 카드에 “핵심 조건 일치 포인트(메인 향/노트/추가 계열)”와 분위기 키워드(있다면)를 함께 출력

### 3.2 페이지 역할

- `01_preference_test.py`
  - 모든 입력 요소를 **DB 기반 selectbox**로 구현 (`scent_categories`, `scents`)
  - Python 리스트/하드코딩 대신 DB 값 사용 → DB 응용 프로젝트의 특징을 강조

- `02_recommendation_result.py`
  - `st.session_state["test_id"]` 기준으로 `recommendation_results`와 `perfumes` 조인 조회
  - Skeleton 단계에서는 “보기 전용 화면”으로 두고, 저장/비교 버튼은 UI만 배치

---

## 4. DB 연동 구조

### 4.1 Supabase 클라이언트

- `database/supabase_client.py`
  - `SUPABASE_URL = st.secrets["SUPABASE_URL"]`
  - `SUPABASE_KEY = st.secrets["SUPABASE_KEY"]`
  - `supabase = create_client(SUPABASE_URL, SUPABASE_KEY)`
  - 다른 모듈은 `from database.supabase_client import supabase` 형태로 재사용

### 4.2 읽기 쿼리 계층

- `scent_repository.py`
  - `get_scent_categories()` → `SELECT * FROM scent_categories ORDER BY category_name`
  - `get_scents_by_category(category_id)` →
    - `SELECT * FROM scents WHERE category_id = :category_id ORDER BY scent_name_ko`

- `recommendation_repository.py`
  - `get_perfume_recommendations_by_test(test_id)` →
    - `JOIN recommendation_results` + `perfumes` + (선택) `perfume_moods` + `mood_keywords`

### 4.3 쓰기 쿼리 계층

- `preference_repository.py`
  - `create_user_preference_test(user_id | None)` →
    - `INSERT INTO user_preference_tests (user_id) VALUES (:user_id) RETURNING test_id`
  - `save_main_choice(test_id, category_id, scent_id, preferred_note_type)`
  - `save_additional_categories(test_id, category_ids)`

- `recommendation_repository.py`
  - `save_recommendation_results(test_id, recommendations)` →
    - Python 쪽에서는 `[{"perfume_id": ..., "recommendation_score": ...}, ...]`
    - DB Insert: `INSERT INTO recommendation_results (test_id, perfume_id, recommendation_score) ...`

---

## 5. SQL 기반 추천 구조

### 5.1 기본 아이디어

- Python 루프가 아닌, 가능한 한 **SQL에서 점수를 계산**하는 구조를 목표로 한다.
- 입력:
  - `:main_scent_id`
  - `:preferred_note_type` (`top/middle/base`)
  - `:additional_category_ids[]` (정수 배열)
- 출력:
  - `perfume_id`
  - `score` (정수)
  - (선택) `main_match`, `note_match`, `additional_match_count` 등 디버깅/설명용 컬럼

### 5.2 추천 점수 정책(문서 반영)

- 메인 향 일치: `+50`
- 메인 향 + note_type 일치: `+30`
- 추가 category 일치(각 계열당): `+10`
- 분위기 일치: `+5` (Skeleton에서는 우선 “점수 계산은 보류”하고, 향후 확장을 위해 칼럼만 고려)

### 5.3 `recommendation_scoring.sql` 초안 구조

```sql
-- recommendation_scoring.sql (개념 스케치)
WITH base AS (
  SELECT
    p.perfume_id,
    -- 메인 향 존재 여부
    MAX(
      CASE WHEN pn.scent_id = :main_scent_id THEN 1 ELSE 0 END
    ) AS has_main_scent,
    -- 메인 향 + note_type 일치 여부
    MAX(
      CASE
        WHEN pn.scent_id = :main_scent_id
         AND pn.note_type = :preferred_note_type
        THEN 1 ELSE 0
      END
    ) AS has_main_scent_with_note,
    -- 추가 category 일치 개수
    COUNT(
      DISTINCT CASE
        WHEN sc.category_id = ANY(:additional_category_ids)
        THEN sc.category_id
        ELSE NULL
      END
    ) AS additional_category_match_count
  FROM perfumes p
  JOIN perfume_notes pn ON pn.perfume_id = p.perfume_id
  JOIN scents s ON s.scent_id = pn.scent_id
  JOIN scent_categories sc ON sc.category_id = s.category_id
  GROUP BY p.perfume_id
),
scored AS (
  SELECT
    perfume_id,
    (has_main_scent * 50)
    + (has_main_scent_with_note * 30)
    + (additional_category_match_count * 10) AS recommendation_score
  FROM base
)
SELECT
  perfume_id,
  recommendation_score
FROM scored
WHERE recommendation_score > 0
ORDER BY recommendation_score DESC, perfume_id ASC
LIMIT 5;
```

- 실제 Supabase에서는:
  - SQL 뷰 또는 Postgres 함수로 변환하거나
  - `sql/`에 저장한 후 문자열로 불러 `supabase.rpc` or `supabase.postgrest.rpc` 등으로 호출하는 패턴 사용

---

## 6. 페이지 구성과 최소 기능 정의

### 6.1 `01_preference_test.py`

- **입력 요소**
  - `selectbox("좋아하는 향 계열", category_names)`
  - `selectbox("좋아하는 향", scents_in_category(scent_name_ko 표시))`
  - `radio("언제 향이 느껴졌으면 좋나요?", ["top", "middle", "base"])`
  - `multiselect("추가로 좋아하는 향 계열", category_names)`
- **로직 흐름**
  1. 카테고리 선택 시 `category_id`를 내부에서 찾기
  2. 해당 `category_id`로 `scents` 조회 후, 사용자가 선택한 scent의 `scent_id` 확보
  3. 추가 계열 선택 시 `category_ids` 리스트 확보
  4. “추천 보기” 버튼 클릭 시:
     - `test_id = create_user_preference_test(user_id=None)`
     - `save_main_choice(test_id, main_category_id, main_scent_id, preferred_note_type)`
     - `save_additional_categories(test_id, additional_category_ids)`
     - `recommendation_service.run_recommendation(test_id, main_scent_id, preferred_note_type, additional_category_ids)`
     - `st.session_state["test_id"] = test_id`

### 6.2 `02_recommendation_result.py`

- **조회**
  - `test_id = st.session_state.get("test_id")` 존재 여부 확인
  - `get_recommendations_by_test(test_id)`로 DB에서 Top 5 조회 (+`perfumes`/`perfume_moods` 조인)
- **표시**
  - 카드 형태:
    - 향수명 / 브랜드명
    - 추천 점수
    - (선택) “일치 조건 요약” 텍스트 (예: `"메인 향 Rose가 middle note로 포함되고, Floral 계열이 추가로 일치합니다."`)

---

## 7. 데이터 표준화 / 향 데이터 처리 원칙

- **Canonical scent 기준**
  - DB는 `scent_name_en`을 canonical로 사용하고, UI에서는 `scent_name_ko` 표시
  - 동의어/표기 차이는 `utils/scent_normalization.py`에서 처리
    - 예: `"패출리"`, `"파출리"` → `"Patchouli"`
    - `"스파이시"`, `"스파이스"` → `"Spicy"`
- **카테고리/노트 타입 통일**
  - `note_type`은 항상 소문자 `'top' | 'middle' | 'base'`
  - 카테고리명은 `scent_categories.category_name` 기준으로만 사용(하드코딩 금지)

---

## 8. Skeleton 단계에서의 포함/제외 기능 정리

- **포함**
  - 비로그인 취향 테스트 1회 실행
  - 테스트 입력값을 DB에 기록 (`user_preference_tests`, `user_test_main_choice`, `user_test_additional_categories`)
  - SQL 기반 추천 점수 계산(메인 향 / note_type / 추가 category)
  - 추천 결과 Top 5 조회 및 카드 UI로 출력

- **제외 (향후 단계 확장 대상)**
  - Supabase Auth 기반 로그인/회원 기능
  - 저장/비교 기능 실제 동작(`saved_perfumes`, 비교 테이블)
  - 비회원 조회코드, 조회 이력 화면
  - 분위기 점수까지 포함한 고급 추천
  - AI/벡터/머신러닝 추천
  - 배포/자동화/고급 캐싱

---

## 9. 요약

- 이 Skeleton 설계는 기존 문서의:
  - `scent_categories → scents → perfume_notes → perfumes`
  - `user_preference_tests → user_test_main_choice/user_test_additional_categories → recommendation_results`
  - 점수 정책(+50/+30/+10(+5))
  를 그대로 따르면서,
- **Streamlit는 UI와 흐름**, **DB/SQL은 스코어링과 데이터 모델**에 집중시키는 구조를 목표로 한다.
- 다음 단계에서는 이 Spec을 기준으로 각 디렉터리/파일을 실제로 생성하고, 최소 동작 가능한 Streamlit 앱 Skeleton을 구현한다.

