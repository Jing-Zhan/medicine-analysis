-- ============================================================
-- 适应症与药品画像：关联强度预计算
--
-- 目的：
--   现有 13 个接口都是描述性统计（谁多用、谁排前），缺关联强度。
--   这里把「适应症 × 药品」的频次预先算好，并把三个分母一起冗余到同一张表，
--   使查询时不用连任何维表就能算出支持度、置信度、提升度。
--
-- 三个统计量的定义（N 为全局处方数）：
--   support(d,g) = cnt(d,g) / N
--   conf(g|d)    = cnt(d,g) / disease_total(d)     得这个病用这个药的概率
--   lift(d,g)    = conf(g|d) / (drug_total(g)/N)   大于 1 表示对该适应症有额外倾向
--
-- 执行：
--   mysql -uroot -p123456 yiyao < agg_profile.sql
--
-- 预计耗时：3~6 分钟
--
-- 写法说明：
--   不用 CREATE TABLE AS SELECT。实测该写法会把 COALESCE 的结果推断成 TEXT，
--   而 TEXT 不能直接建普通索引，会报 ERROR 1170。
--   这里统一显式建表，插入时用 LEFT(..., n) 截断到定长，保证列类型与索引可用。
--
-- 本脚本只新增 agg_ 前缀的表，不改动任何业务表。
-- ============================================================

-- ---------------------------------------------------------------- 1. 适应症边际分布

DROP TABLE IF EXISTS agg_disease_total;
CREATE TABLE agg_disease_total (
  disease_code VARCHAR(64)  NOT NULL,
  disease_name VARCHAR(255) DEFAULT NULL,
  cnt          INT          NOT NULL DEFAULT 0,
  amount       DOUBLE       NOT NULL DEFAULT 0,
  PRIMARY KEY (disease_code),
  KEY idx_disease_name (disease_name(48))
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO agg_disease_total (disease_code, disease_name, cnt, amount)
SELECT p.m_diagnostic1,
       LEFT(COALESCE(NULLIF(d.disease_type_name13, ''), p.m_diagnostic1), 255),
       COUNT(*),
       ROUND(SUM(p.amount), 2)
FROM prescription_diseases p
LEFT JOIN t_view_disease d ON p.m_diagnostic1 = d.disease_type13
WHERE p.m_diagnostic1 IS NOT NULL AND p.m_diagnostic1 <> ''
GROUP BY 1, 2;

-- ---------------------------------------------------------------- 2. 药品边际分布

DROP TABLE IF EXISTS agg_drug_total;
CREATE TABLE agg_drug_total (
  drug_code VARCHAR(64)  NOT NULL,
  drug_name VARCHAR(255) DEFAULT NULL,
  cnt       INT          NOT NULL DEFAULT 0,
  amount    DOUBLE       NOT NULL DEFAULT 0,
  PRIMARY KEY (drug_code),
  KEY idx_drug_name (drug_name(48))
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO agg_drug_total (drug_code, drug_name, cnt, amount)
SELECT p.drug_code,
       LEFT(COALESCE(NULLIF(g.drug_generic_name, ''), p.drug_code), 255),
       COUNT(*),
       ROUND(SUM(p.amount), 2)
FROM prescription_diseases p
LEFT JOIN t_view_drug g ON p.drug_code = g.drug
WHERE p.drug_code IS NOT NULL AND p.drug_code <> ''
GROUP BY 1, 2;

-- ---------------------------------------------------------------- 3. 组合频次

DROP TABLE IF EXISTS agg_pair;
CREATE TABLE agg_pair (
  disease_code VARCHAR(64) NOT NULL,
  drug_code    VARCHAR(64) NOT NULL,
  cnt          INT         NOT NULL DEFAULT 0,
  PRIMARY KEY (disease_code, drug_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO agg_pair (disease_code, drug_code, cnt)
SELECT p.m_diagnostic1, p.drug_code, COUNT(*)
FROM prescription_diseases p
WHERE p.m_diagnostic1 IS NOT NULL AND p.m_diagnostic1 <> ''
  AND p.drug_code IS NOT NULL AND p.drug_code <> ''
GROUP BY 1, 2;

-- ---------------------------------------------------------------- 4. 画像主表

DROP TABLE IF EXISTS agg_disease_drug;
CREATE TABLE agg_disease_drug (
  disease_code  VARCHAR(64)  NOT NULL,
  drug_code     VARCHAR(64)  NOT NULL,
  disease_name  VARCHAR(255) DEFAULT NULL,
  drug_name     VARCHAR(255) DEFAULT NULL,
  cnt           INT          NOT NULL DEFAULT 0,
  disease_total INT          NOT NULL DEFAULT 0,
  drug_total    INT          NOT NULL DEFAULT 0,
  grand_total   INT          NOT NULL DEFAULT 0,
  PRIMARY KEY (disease_code, drug_code),
  KEY idx_drug_cnt (drug_code, cnt),
  KEY idx_disease_cnt (disease_code, cnt)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO agg_disease_drug
  (disease_code, drug_code, disease_name, drug_name, cnt, disease_total, drug_total, grand_total)
SELECT a.disease_code,
       a.drug_code,
       dt.disease_name,
       dg.drug_name,
       a.cnt,
       dt.cnt,
       dg.cnt,
       (SELECT COALESCE(SUM(cnt), 0) FROM agg_disease_total)
FROM agg_pair a
JOIN agg_disease_total dt ON dt.disease_code = a.disease_code
JOIN agg_drug_total    dg ON dg.drug_code    = a.drug_code;

DROP TABLE agg_pair;

-- ---------------------------------------------------------------- 5. 处方用药明细

-- 用于联合用药：与该药出现在同一处方里的其他药
DROP TABLE IF EXISTS agg_pres_drug;
CREATE TABLE agg_pres_drug (
  pid       VARCHAR(128) NOT NULL,
  drug_code VARCHAR(64)  NOT NULL,
  KEY idx_pid (pid),
  KEY idx_drug (drug_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO agg_pres_drug (pid, drug_code)
SELECT DISTINCT LEFT(m_prescription_id, 128), drug_code
FROM prescription_diseases
WHERE m_prescription_id IS NOT NULL AND m_prescription_id <> ''
  AND drug_code IS NOT NULL AND drug_code <> '';

-- ---------------------------------------------------------------- 6. 校验

SELECT 'disease_total' AS tbl, COUNT(*) AS rows_cnt FROM agg_disease_total
UNION ALL SELECT 'drug_total',   COUNT(*) FROM agg_drug_total
UNION ALL SELECT 'disease_drug', COUNT(*) FROM agg_disease_drug
UNION ALL SELECT 'pres_drug',    COUNT(*) FROM agg_pres_drug;

-- 抽查：样本量足够且提升度最高的五个「适应症 × 药品」组合
SELECT LEFT(disease_name, 24) AS disease_name,
       LEFT(drug_name, 12)    AS drug_name,
       cnt,
       ROUND(cnt / disease_total, 4)                               AS conf,
       ROUND((cnt / disease_total) / (drug_total / grand_total), 3) AS lift
FROM agg_disease_drug
WHERE cnt >= 50
ORDER BY lift DESC
LIMIT 5;
