# Streamlit Cloud 배포 가이드

## 1. GitHub 확인

저장소: https://github.com/mun8-8/perfume_database  
메인 파일: `app.py`  
Python 의존성: `requirements.txt`

## 2. Streamlit Cloud에서 앱 만들기

1. https://share.streamlit.io 접속 후 GitHub 로그인
2. **New app** 클릭
3. 설정:
   - **Repository:** `mun8-8/perfume_database`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. **Advanced settings** → **Secrets** 에 아래 내용 붙여넣기:

```toml
SUPABASE_URL = "https://ugqhedyaefmpdzqujxgw.supabase.co"
SUPABASE_KEY = "여기에_Supabase_anon_또는_publishable_키"
```

로컬 `.streamlit/secrets.toml` 내용을 그대로 복사해도 됩니다.

5. **Deploy** 클릭

## 3. 배포 후 URL

배포가 끝나면 다음 형태의 공개 URL이 생성됩니다:

`https://perfume-database-xxxx.streamlit.app`

(앱 이름에 따라 주소가 달라집니다.)

## 4. Supabase 확인 (필수)

Supabase 대시보드에서 아래 SQL이 실행되어 있어야 합니다.

- `sql/auth_schema.sql` / `fix_users_rls.sql`
- `sql/nine_categories_seed.sql`
- `sql/recommendation_scoring.sql`
- `sql/member_data_rls.sql`
- (선택) `scripts/generated_seed.sql`

**Authentication → Providers → Email** 에서 **Confirm email** 을 끄면 회원가입 후 바로 로그인 테스트가 쉽습니다.

## 5. 문제 해결

| 증상 | 해결 |
|------|------|
| secrets 오류 | Cloud 앱 Settings → Secrets 다시 저장 |
| RLS 오류 | `member_data_rls.sql`, `fix_users_rls.sql` 실행 |
| 추천 결과 없음 | `recommendation_scoring.sql`, 향수 시드 확인 |
