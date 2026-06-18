-- Supabase SQL Editor 에서 1회 실행하세요.
-- 가중치: 주향 30 + 세부향 30 + 발향시점 20 + 보조향 20 = 100

CREATE OR REPLACE FUNCTION recommend_perfumes(
  p_main_category_id INTEGER,
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
      MAX(
        CASE WHEN sc.category_id = p_main_category_id THEN 1 ELSE 0 END
      ) AS has_main_category,
      MAX(
        CASE WHEN pn.scent_id = p_main_scent_id THEN 1 ELSE 0 END
      ) AS has_detail_scent,
      MAX(
        CASE
          WHEN pn.scent_id = p_main_scent_id
           AND pn.note_type = p_preferred_note_type
          THEN 1 ELSE 0
        END
      ) AS has_note_match,
      MAX(
        CASE
          WHEN sc.category_id = ANY (p_additional_category_ids)
           AND sc.category_id <> p_main_category_id
          THEN 1 ELSE 0
        END
      ) AS has_sub_category
    FROM perfumes p
    JOIN perfume_notes pn ON pn.perfume_id = p.perfume_id
    JOIN scents s ON s.scent_id = pn.scent_id
    JOIN scent_categories sc ON sc.category_id = s.category_id
    GROUP BY p.perfume_id
  ),
  scored AS (
    SELECT
      perfume_id,
      (has_main_category * 30)
        + (has_detail_scent * 30)
        + (has_note_match * 20)
        + (has_sub_category * 20) AS recommendation_score
    FROM base
  )
  SELECT perfume_id, recommendation_score::INTEGER
  FROM scored
  WHERE recommendation_score > 0
  ORDER BY recommendation_score DESC, perfume_id ASC
  LIMIT 5;
$$;
