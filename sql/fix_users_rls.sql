-- users 테이블 RLS 오류 수정 (Supabase SQL Editor에서 1회 실행)
-- 오류: new row violates row-level security policy for table "users"

-- 1) 권한 부여
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.users TO authenticated;

-- 2) RLS 정책 재설정
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "users_select_own" ON public.users;
CREATE POLICY "users_select_own"
  ON public.users FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "users_insert_own" ON public.users;
CREATE POLICY "users_insert_own"
  ON public.users FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "users_update_own" ON public.users;
CREATE POLICY "users_update_own"
  ON public.users FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- 3) 로그인 JWT 기준 프로필 저장 RPC (RLS 우회)
CREATE OR REPLACE FUNCTION public.upsert_user_profile(
  p_email TEXT,
  p_nickname TEXT
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF auth.uid() IS NULL THEN
    RAISE EXCEPTION 'not authenticated';
  END IF;

  INSERT INTO public.users (user_id, email, nickname)
  VALUES (auth.uid(), p_email, p_nickname)
  ON CONFLICT (user_id) DO UPDATE
    SET email = EXCLUDED.email,
        nickname = EXCLUDED.nickname;
END;
$$;

GRANT EXECUTE ON FUNCTION public.upsert_user_profile(TEXT, TEXT) TO authenticated;

-- 4) 닉네임 변경 RPC (RLS 우회)
CREATE OR REPLACE FUNCTION public.update_user_nickname(p_nickname TEXT)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF auth.uid() IS NULL THEN
    RAISE EXCEPTION 'not authenticated';
  END IF;
  IF p_nickname IS NULL OR trim(p_nickname) = '' THEN
    RAISE EXCEPTION 'nickname required';
  END IF;

  UPDATE public.users
  SET nickname = trim(p_nickname)
  WHERE user_id = auth.uid();

  IF NOT FOUND THEN
    INSERT INTO public.users (user_id, email, nickname)
    SELECT auth.uid(), u.email, trim(p_nickname)
    FROM auth.users u
    WHERE u.id = auth.uid();
  END IF;
END;
$$;

GRANT EXECUTE ON FUNCTION public.update_user_nickname(TEXT) TO authenticated;
