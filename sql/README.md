# SQL 설정

1. Supabase 대시보드 → **SQL Editor** 로 이동
2. (최초 1회) `auth_schema.sql` — `users` 테이블, Auth 가입 트리거, RLS
   - RLS 오류 시: `fix_users_rls.sql` 실행
3. (최초 1회) `nine_categories_seed.sql` — 9개 주향 계열 + 36개 세부향
4. (선택) `scripts/generated_seed.sql` — 엑셀 향수·노트 데이터 (`python scripts/excel_to_seed.py` 로 재생성)
5. `recommendation_scoring.sql` — 추천 RPC (가중치: 주향 30 / 세부향 30 / 발향 20 / 보조향 20)
6. `member_data_rls.sql` — 회원 이력·즐겨찾기 RLS (이력 저장 오류 시 실행)

**인증 개발 팁:** Supabase 대시보드 → Authentication → Providers → Email 에서 **Confirm email** 을 끄면 로컬에서 즉시 로그인 테스트가 가능합니다.

**주향·세부향 기준:** `utils/scent_catalog.py` (앱·시드·엑셀 변환 공통)

`recommendation_scoring.sql` 을 갱신했다면 Supabase SQL Editor 에서 **다시 실행**해야 합니다.
