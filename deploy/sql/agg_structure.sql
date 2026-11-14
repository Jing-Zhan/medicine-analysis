-- ============================================================
-- 用药结构对比：科室维度与疾病大类维度
--
-- 背景：
--   这份数据的价格基本恒定（总额 26,239,620.54 除以 100 万行约等于 26.24 元），
--   药品与适应症逐行随机配对，处方号几乎一行一个。
--   因此费用分析、关联分析、联合用药都没有区分度。
--   能形成有效差异的只有「类别构成」：不同科室、不同疾病大类的剂型结构与
--   基本药物结构差别明显，这才是药事管理实际会看的东西。
--
-- 两张表分别按科室、疾病大类把药品用量提前聚合，查询时再与药品维表关联，
-- 算出注射剂占比、基本药物占比、抗菌药物占比。
--
-- 执行：
--   mysql -uroot -p123456 yiyao < agg_structure.sql
--
-- 预计耗时：1~2 分钟
-- 本脚本只新增 agg_ 前缀的表，不改动业务表。
-- ============================================================

-- ---------------------------------------------------------------- 1. 科室 × 药品

DROP TABLE IF EXISTS agg_section_drug;
CREATE TABLE agg_section_drug (
  section_name VARCHAR(64) NOT NULL,
  drug_code    VARCHAR(64) NOT NULL,
  cnt          INT         NOT NULL DEFAULT 0,
  PRIMARY KEY (section_name, drug_code),
  KEY idx_drug (drug_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO agg_section_drug (section_name, drug_code, cnt)
SELECT LEFT(COALESCE(NULLIF(s.section_name1, ''), '未标注'), 64), p.drug_code, COUNT(*)
FROM prescription_diseases p
JOIN t_view_section s ON p.m_section = s.section2
WHERE p.drug_code IS NOT NULL AND p.drug_code <> ''
GROUP BY 1, 2;

-- ---------------------------------------------------------------- 2. 疾病大类 × 药品

DROP TABLE IF EXISTS agg_cat_drug;
CREATE TABLE agg_cat_drug (
  cat_code  VARCHAR(16)  NOT NULL,
  cat_name  VARCHAR(255) DEFAULT NULL,
  drug_code VARCHAR(64)  NOT NULL,
  cnt       INT          NOT NULL DEFAULT 0,
  PRIMARY KEY (cat_code, drug_code),
  KEY idx_drug (drug_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO agg_cat_drug (cat_code, cat_name, drug_code, cnt)
SELECT d.disease_type11,
       LEFT(COALESCE(NULLIF(d.disease_type_name11, ''), '未分类'), 255),
       p.drug_code,
       COUNT(*)
FROM prescription_diseases p
JOIN t_view_disease d ON p.m_diagnostic1 = d.disease_type13
WHERE p.drug_code IS NOT NULL AND p.drug_code <> ''
GROUP BY 1, 2, 3;

-- ---------------------------------------------------------------- 3. 校验

SELECT 'section_drug' AS tbl, COUNT(*) AS rows_cnt FROM agg_section_drug
UNION ALL SELECT 'cat_drug', COUNT(*) FROM agg_cat_drug;

-- 抽查：前五个科室的用药结构，看差异是否真实存在
SELECT x.section_name AS 科室,
       SUM(x.cnt) AS 处方数,
       ROUND(SUM(CASE WHEN g.form_name1 LIKE '%注射%' THEN x.cnt ELSE 0 END) * 100.0 / SUM(x.cnt), 2) AS 注射剂占比,
       ROUND(SUM(CASE WHEN g.is_essential_drug = '是' THEN x.cnt ELSE 0 END) * 100.0 / SUM(x.cnt), 2) AS 基本药物占比,
       ROUND(SUM(CASE WHEN g.drug_generic_name REGEXP '霉素|西林|头孢|沙星|环素|培南|硝唑|磺胺|呋喃'
                 THEN x.cnt ELSE 0 END) * 100.0 / SUM(x.cnt), 2) AS 抗菌药物占比
FROM agg_section_drug x
JOIN t_view_drug g ON x.drug_code = g.drug
GROUP BY 1
ORDER BY 2 DESC
LIMIT 5;
