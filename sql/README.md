# SQL 설정

1. Supabase 대시보드 → **SQL Editor** 로 이동
2. (최초 1회) `auth_schema.sql` — `users` 테이블, Auth 가입 트리거, RLS
   - RLS 오류 시: `fix_users_rls.sql` 실행
3. (최초 1회) `nine_categories_seed.sql` — 9개 주향 계열 + 36개 세부향
4. (선택) `scripts/generated_seed.sql` — 엑셀 향수·노트 데이터 (`python scripts/excel_to_seed.py` 로 재생성)
5. `recommendation_scoring.sql` — 추천 RPC 함수

**인증 개발 팁:** Supabase 대시보드 → Authentication → Providers → Email 에서 **Confirm email** 을 끄면 로컬에서 즉시 로그인 테스트가 가능합니다.

**주향·세부향 기준:** `utils/scent_catalog.py` (앱·시드·엑셀 변환 공통)

함수를 아직 만들지 않았어도 앱은 **동일 점수 규칙**의 Python fallback 으로 동작합니다.
