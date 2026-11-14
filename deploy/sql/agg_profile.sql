-- ============================================================
-- 适应症与药品画像：关联强度预计算
--
-- 目的：
--   现有 13 个接口都是描述性统计（谁多用、谁排前），缺关联强度。
--   这里把「适应症 × 药品」的频次预先算好，并把三个分母一起冗余到同一张表，
--   使查询时不用连任何维表就能算出支持度、置信度、提升度。
--
-- 四个统计量的定义（N 为全局处方数）：
--   support(d,g) = cnt(d,g) / N
--   conf(g|d)    = cnt(d,g) / disease_total(d)     得这个病用这个药的概率
--   lift(d,g)    = conf(g|d) / (drug_total(g)/N)   大于 1 表示对该适应症有额外倾向
--
-- 执行：
--   mysql -uroot -p123456 yiyao < agg_profile.sql
--
-- 预计耗时：3~6 分钟（100 万行两次分组聚合 + 一次两表关联）
-- 磁盘占用：约 80~150 MB
--
-- 注意：本脚本只新增 agg_ 前缀的表，不改动任何业务表。
-- ============================================================

-- ---------------------------------------------------------------- 1. 边际分布

DROP TABLE IF EXISTS agg_disease_total;
CREATE TABLE agg_disease_total AS
SELECT p.m_diagnostic1                                        AS disease_code,
       COALESCE(NULLIF(d.disease_type_name13, ''), p.m_diagnostic1) AS disease_name,
       COUNT(*)                                               AS cnt,
       ROUND(SUM(p.amount), 2)                                AS amount
FROM prescription_diseases p
LEFT JOIN t_view_disease d ON p.m_diagnostic1 = d.disease_type13
WHERE p.m_diagnostic1 IS NOT NULL AND p.m_diagnostic1 <> ''
GROUP BY 1, 2;
ALTER TABLE agg_disease_total ADD PRIMARY KEY (disease_code);
ALTER TABLE agg_disease_total ADD KEY idx_name (disease_name);

DROP TABLE IF EXISTS agg_drug_total;
CREATE TABLE agg_drug_total AS
SELECT p.drug_code                                            AS drug_code,
       COALESCE(NULLIF(g.drug_generic_name, ''), p.drug_code)  AS drug_name,
       COUNT(*)                                               AS cnt,
       ROUND(SUM(p.amount), 2)                                AS amount
FROM prescription_diseases p
LEFT JOIN t_view_drug g ON p.drug_code = g.drug
WHERE p.drug_code IS NOT NULL AND p.drug_code <> ''
GROUP BY 1, 2;
ALTER TABLE agg_drug_total ADD PRIMARY KEY (drug_code);
ALTER TABLE agg_drug_total ADD KEY idx_name (drug_name);

-- ---------------------------------------------------------------- 2. 组合频次

DROP TABLE IF EXISTS agg_pair;
CREATE TABLE agg_pair AS
SELECT p.m_diagnostic1 AS disease_code,
       p.drug_code     AS drug_code,
       COUNT(*)        AS cnt
FROM prescription_diseases p
WHERE p.m_diagnostic1 IS NOT NULL AND p.m_diagnostic1 <> ''
  AND p.drug_code IS NOT NULL AND p.drug_code <> ''
GROUP BY 1, 2;

-- ---------------------------------------------------------------- 3. 画像主表

DROP TABLE IF EXISTS agg_disease_drug;
CREATE TABLE agg_disease_drug AS
SELECT a.disease_code,
       a.drug_code,
       dt.disease_name,
       dg.drug_name,
       a.cnt,
       dt.cnt          AS disease_total,
       dg.cnt          AS drug_total,
       (SELECT SUM(cnt) FROM agg_disease_total) AS grand_total
FROM agg_pair a
JOIN agg_disease_total dt ON dt.disease_code = a.disease_code
JOIN agg_drug_total    dg ON dg.drug_code    = a.drug_code;

ALTER TABLE agg_disease_drug ADD PRIMARY KEY (disease_code, drug_code);
ALTER TABLE agg_disease_drug ADD KEY idx_drug_cnt (drug_code, cnt);
ALTER TABLE agg_disease_drug ADD KEY idx_disease_cnt (disease_code, cnt);

DROP TABLE agg_pair;

-- ---------------------------------------------------------------- 4. 处方用药明细

-- 用于联合用药：与该药出现在同一处方里的其他药
DROP TABLE IF EXISTS agg_pres_drug;
CREATE TABLE agg_pres_drug AS
SELECT DISTINCT m_prescription_id AS pid, drug_code
FROM prescription_diseases
WHERE m_prescription_id IS NOT NULL AND m_prescription_id <> ''
  AND drug_code IS NOT NULL AND drug_code <> '';

ALTER TABLE agg_pres_drug ADD KEY idx_pid (pid);
ALTER TABLE agg_pres_drug ADD KEY idx_drug (drug_code);

-- ---------------------------------------------------------------- 5. 校验

SELECT 'disease_total' AS tbl, COUNT(*) AS rows_cnt FROM agg_disease_total
UNION ALL SELECT 'drug_total',   COUNT(*) FROM agg_drug_total
UNION ALL SELECT 'disease_drug', COUNT(*) FROM agg_disease_drug
UNION ALL SELECT 'pres_drug',    COUNT(*) FROM agg_pres_drug;

-- 抽查：样本量足够且提升度最高的五个「适应症 × 药品」组合
SELECT disease_name, drug_name, cnt,
       ROUND(cnt / disease_total, 4)                        AS conf,
       ROUND((cnt / disease_total) / (drug_total / grand_total), 3) AS lift
FROM agg_disease_drug
WHERE cnt >= 50
ORDER BY lift DESC
LIMIT 5;
