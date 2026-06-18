-- 회원 취향 테스트 · 추천 결과 · 즐겨찾기 RLS (Supabase SQL Editor 1회 실행)

GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- user_preference_tests
ALTER TABLE public.user_preference_tests ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "tests_select_own" ON public.user_preference_tests;
CREATE POLICY "tests_select_own"
  ON public.user_preference_tests FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

DROP POLICY IF EXISTS "tests_insert_own" ON public.user_preference_tests;
CREATE POLICY "tests_insert_own"
  ON public.user_preference_tests FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

-- user_test_main_choice
ALTER TABLE public.user_test_main_choice ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "main_choice_select" ON public.user_test_main_choice;
CREATE POLICY "main_choice_select"
  ON public.user_test_main_choice FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.user_preference_tests t
      WHERE t.test_id = user_test_main_choice.test_id
        AND t.user_id = auth.uid()
    )
  );

DROP POLICY IF EXISTS "main_choice_insert" ON public.user_test_main_choice;
CREATE POLICY "main_choice_insert"
  ON public.user_test_main_choice FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.user_preference_tests t
      WHERE t.test_id = user_test_main_choice.test_id
        AND t.user_id = auth.uid()
    )
  );

-- user_test_additional_categories
ALTER TABLE public.user_test_additional_categories ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "add_cat_select" ON public.user_test_additional_categories;
CREATE POLICY "add_cat_select"
  ON public.user_test_additional_categories FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.user_preference_tests t
      WHERE t.test_id = user_test_additional_categories.test_id
        AND t.user_id = auth.uid()
    )
  );

DROP POLICY IF EXISTS "add_cat_insert" ON public.user_test_additional_categories;
CREATE POLICY "add_cat_insert"
  ON public.user_test_additional_categories FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.user_preference_tests t
      WHERE t.test_id = user_test_additional_categories.test_id
        AND t.user_id = auth.uid()
    )
  );

-- recommendation_results
ALTER TABLE public.recommendation_results ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "rec_results_select" ON public.recommendation_results;
CREATE POLICY "rec_results_select"
  ON public.recommendation_results FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.user_preference_tests t
      WHERE t.test_id = recommendation_results.test_id
        AND t.user_id = auth.uid()
    )
  );

DROP POLICY IF EXISTS "rec_results_insert" ON public.recommendation_results;
CREATE POLICY "rec_results_insert"
  ON public.recommendation_results FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.user_preference_tests t
      WHERE t.test_id = recommendation_results.test_id
        AND t.user_id = auth.uid()
    )
  );

-- saved_perfumes (즐겨찾기)
ALTER TABLE public.saved_perfumes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "saved_select_own" ON public.saved_perfumes;
CREATE POLICY "saved_select_own"
  ON public.saved_perfumes FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

DROP POLICY IF EXISTS "saved_insert_own" ON public.saved_perfumes;
CREATE POLICY "saved_insert_own"
  ON public.saved_perfumes FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS "saved_delete_own" ON public.saved_perfumes;
CREATE POLICY "saved_delete_own"
  ON public.saved_perfumes FOR DELETE
  TO authenticated
  USING (user_id = auth.uid());

DROP POLICY IF EXISTS "saved_update_own" ON public.saved_perfumes;
CREATE POLICY "saved_update_own"
  ON public.saved_perfumes FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid());
