-- Supabase Auth 연동용 users 테이블 및 RLS 정책
-- Supabase SQL Editor에서 실행하세요.

-- 1) public.users 프로필 테이블
CREATE TABLE IF NOT EXISTS public.users (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email VARCHAR(255) UNIQUE NOT NULL,
  nickname VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2) auth.users 가입 시 public.users 자동 생성 트리거
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  INSERT INTO public.users (user_id, email, nickname)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'nickname', split_part(NEW.email, '@', 1))
  )
  ON CONFLICT (user_id) DO UPDATE
    SET email = EXCLUDED.email,
        nickname = COALESCE(EXCLUDED.nickname, public.users.nickname);
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- 3) RLS: 본인 프로필만 읽기/수정
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.users TO authenticated;

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

-- 4) 로그인 JWT 기준 프로필 저장 RPC
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

-- 5) 닉네임 변경 RPC (RLS 우회)
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
