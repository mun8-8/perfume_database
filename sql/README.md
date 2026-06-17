# SQL 설정

1. Supabase 대시보드 → **SQL Editor** 로 이동
2. (최초 1회) `nine_categories_seed.sql` — 9개 주향 계열 + 36개 세부향
3. (선택) `scripts/generated_seed.sql` — 엑셀 향수·노트 데이터 (`python scripts/excel_to_seed.py` 로 재생성)
4. `recommendation_scoring.sql` — 추천 RPC 함수

**주향·세부향 기준:** `utils/scent_catalog.py` (앱·시드·엑셀 변환 공통)

함수를 아직 만들지 않았어도 앱은 **동일 점수 규칙**의 Python fallback 으로 동작합니다.
