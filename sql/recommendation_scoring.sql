-- Supabase SQL Editor 에서 1회 실행하세요.
-- Streamlit 앱은 recommend_perfumes RPC 를 우선 호출합니다.

CREATE OR REPLACE FUNCTION recommend_perfumes(
  p_main_scent_id INTEGER,
  p_preferred_note_type TEXT,
  p_additional_category_ids INTEGER[] DEFAULT '{}'
)
RETURNS TABLE (
  perfume_id INTEGER,
  recommendation_score INTEGER
)
LANGUAGE sql
STABLE
AS $$
  WITH base AS (
    SELECT
      p.perfume_id,
      MAX(CASE WHEN pn.scent_id = p_main_scent_id THEN 1 ELSE 0 END) AS has_main_scent,
      MAX(
        CASE
          WHEN pn.scent_id = p_main_scent_id
           AND pn.note_type = p_preferred_note_type
          THEN 1 ELSE 0
        END
      ) AS has_main_scent_with_note,
      COUNT(
        DISTINCT CASE
          WHEN sc.category_id = ANY (p_additional_category_ids)
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
  SELECT perfume_id, recommendation_score::INTEGER
  FROM scored
  WHERE recommendation_score > 0
  ORDER BY recommendation_score DESC, perfume_id ASC
  LIMIT 5;
$$;
