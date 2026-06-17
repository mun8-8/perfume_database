-- 최소 실행용 샘플 데이터
-- 목적: Streamlit Skeleton이 바로 동작하도록 핵심 테이블에 최소 데이터 주입
-- 전제: 테이블(DDL)은 이미 생성되어 있어야 합니다.

BEGIN;

-- 1) 향 계열
INSERT INTO scent_categories (category_name)
VALUES
  ('Floral'),
  ('Woody'),
  ('Citrus')
ON CONFLICT (category_name) DO NOTHING;

-- 2) 세부 향 (canonical en + ko)
INSERT INTO scents (category_id, scent_name_en, scent_name_ko)
SELECT c.category_id, v.scent_name_en, v.scent_name_ko
FROM (
  VALUES
    ('Floral', 'Rose', '장미'),
    ('Floral', 'Jasmine', '자스민'),
    ('Woody', 'Sandalwood', '샌달우드'),
    ('Woody', 'Patchouli', '패출리'),
    ('Citrus', 'Bergamot', '베르가못'),
    ('Citrus', 'Lemon', '레몬')
) AS v(category_name, scent_name_en, scent_name_ko)
JOIN scent_categories c ON c.category_name = v.category_name
ON CONFLICT (scent_name_en) DO NOTHING;

-- 3) 향수 기본 정보
-- perfumes에 UNIQUE 제약이 없을 수 있으므로 WHERE NOT EXISTS로 중복 방지
INSERT INTO perfumes (perfume_name, brand_name)
SELECT 'Floral Dawn', 'Sample Brand'
WHERE NOT EXISTS (
  SELECT 1 FROM perfumes WHERE perfume_name = 'Floral Dawn' AND brand_name = 'Sample Brand'
);

INSERT INTO perfumes (perfume_name, brand_name)
SELECT 'Woody Night', 'Sample Brand'
WHERE NOT EXISTS (
  SELECT 1 FROM perfumes WHERE perfume_name = 'Woody Night' AND brand_name = 'Sample Brand'
);

INSERT INTO perfumes (perfume_name, brand_name)
SELECT 'Citrus Breeze', 'Sample Brand'
WHERE NOT EXISTS (
  SELECT 1 FROM perfumes WHERE perfume_name = 'Citrus Breeze' AND brand_name = 'Sample Brand'
);

-- 4) 향수 노트 구성
-- UNIQUE(perfume_id, scent_id, note_type) 전제
WITH p AS (
  SELECT perfume_id, perfume_name
  FROM perfumes
  WHERE (perfume_name, brand_name) IN (
    ('Floral Dawn', 'Sample Brand'),
    ('Woody Night', 'Sample Brand'),
    ('Citrus Breeze', 'Sample Brand')
  )
),
s AS (
  SELECT scent_id, scent_name_en
  FROM scents
  WHERE scent_name_en IN ('Rose', 'Jasmine', 'Sandalwood', 'Patchouli', 'Bergamot', 'Lemon')
)
INSERT INTO perfume_notes (perfume_id, scent_id, note_type)
SELECT p.perfume_id, s.scent_id, v.note_type
FROM (
  VALUES
    ('Floral Dawn', 'Bergamot', 'top'),
    ('Floral Dawn', 'Rose', 'middle'),
    ('Floral Dawn', 'Patchouli', 'base'),
    ('Woody Night', 'Lemon', 'top'),
    ('Woody Night', 'Sandalwood', 'middle'),
    ('Woody Night', 'Patchouli', 'base'),
    ('Citrus Breeze', 'Lemon', 'top'),
    ('Citrus Breeze', 'Jasmine', 'middle'),
    ('Citrus Breeze', 'Sandalwood', 'base')
) AS v(perfume_name, scent_name_en, note_type)
JOIN p ON p.perfume_name = v.perfume_name
JOIN s ON s.scent_name_en = v.scent_name_en
ON CONFLICT (perfume_id, scent_id, note_type) DO NOTHING;

COMMIT;

-- 확인 쿼리 (선택)
-- SELECT * FROM scent_categories ORDER BY category_name;
-- SELECT scent_name_en, scent_name_ko FROM scents ORDER BY scent_name_en;
-- SELECT perfume_name, brand_name FROM perfumes ORDER BY perfume_id;
-- SELECT pn.perfume_id, p.perfume_name, s.scent_name_en, pn.note_type
-- FROM perfume_notes pn
-- JOIN perfumes p ON p.perfume_id = pn.perfume_id
-- JOIN scents s ON s.scent_id = pn.scent_id
-- ORDER BY p.perfume_name, pn.note_type;
