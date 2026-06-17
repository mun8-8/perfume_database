-- 9개 향 계열 + 세부향 (36개) 시드
-- 전제: scent_categories, scents 테이블이 이미 존재합니다.
-- Supabase SQL Editor에서 실행하세요.

BEGIN;

INSERT INTO scent_categories (category_name)
VALUES
  ('시트러스'),
  ('그린'),
  ('프루티'),
  ('플로럴'),
  ('머스크'),
  ('아쿠아틱'),
  ('구르망'),
  ('오리엔탈'),
  ('우디')
ON CONFLICT (category_name) DO NOTHING;

INSERT INTO scents (category_id, scent_name_en, scent_name_ko)
SELECT c.category_id, v.scent_name_en, v.scent_name_ko
FROM (
  VALUES
    ('시트러스', 'Lemon', '레몬'),
    ('시트러스', 'Orange', '오렌지'),
    ('시트러스', 'Grapefruit', '자몽'),
    ('시트러스', 'Bergamot', '베르가못'),
    ('그린', 'Grass Leaf', '풀잎'),
    ('그린', 'Bamboo', '대나무'),
    ('그린', 'Green Tea', '녹차'),
    ('그린', 'Fig Leaf', '무화과 잎'),
    ('프루티', 'Peach', '복숭아'),
    ('프루티', 'Apple', '사과'),
    ('프루티', 'Pear', '배'),
    ('프루티', 'Berry', '베리'),
    ('플로럴', 'Rose', '장미'),
    ('플로럴', 'Jasmine', '자스민'),
    ('플로럴', 'Lily', '백합'),
    ('플로럴', 'Ylang Ylang', '일랑일랑'),
    ('머스크', 'White Musk', '화이트 머스크'),
    ('머스크', 'Clean Musk', '클린 머스크'),
    ('머스크', 'Amber Musk', '앰버 머스크'),
    ('머스크', 'Powdery Musk', '파우더리 머스크'),
    ('아쿠아틱', 'Sea Salt', '씨솔트'),
    ('아쿠아틱', 'Water', '워터'),
    ('아쿠아틱', 'Ozone', '오존'),
    ('아쿠아틱', 'Marine Note', '마린노트'),
    ('구르망', 'Vanilla', '바닐라'),
    ('구르망', 'Chocolate', '초콜릿'),
    ('구르망', 'Caramel', '캐러멜'),
    ('구르망', 'Coffee', '커피'),
    ('오리엔탈', 'Amber', '앰버'),
    ('오리엔탈', 'Incense', '인센스'),
    ('오리엔탈', 'Spice', '스파이스'),
    ('오리엔탈', 'Resin', '레진'),
    ('우디', 'Sandalwood', '샌달우드'),
    ('우디', 'Cedarwood', '시더우드'),
    ('우디', 'Vetiver', '베티버'),
    ('우디', 'Patchouli', '패출리')
) AS v(category_name, scent_name_en, scent_name_ko)
JOIN scent_categories c ON c.category_name = v.category_name
ON CONFLICT (scent_name_en) DO NOTHING;

COMMIT;
