-- ============================================================
-- yiyao 库：为 12 个业务接口补索引（MySQL 5.7.28）
--
-- 背景：
--   12 个接口的 SQL 要在药品（23 万）、诊断（4.2 万）等高基数字段上做关联，
--   走 Kylin 需要预计算 2^22 量级 cuboid，不可行；改为在 MySQL 明细库上执行。
--
-- 本脚本做三件事：
--   1. 补一个生成列 drug_code（去药品码的 _序号 后缀）+ 索引，让药品关联能走索引
--   2. 给事实表的常用分组列补索引
--   3. 给 5 张维表的关联键补索引
--
-- 执行方式：
--   mysql -uroot -p123456 yiyao < mysql_indexes.sql
--
-- 注意：如果某个索引已存在会报 Duplicate key name，忽略即可。
-- ============================================================

-- ---------- 1. 药品码生成列 + 索引 ----------
-- 明细表 m_drug 形如 DM0000178036_2，维表 t_view_drug.drug 是 DM0000178036
ALTER TABLE prescription_diseases
  ADD COLUMN drug_code VARCHAR(64)
  GENERATED ALWAYS AS (SUBSTRING_INDEX(m_drug, '_', 1)) STORED;

CREATE INDEX idx_drug_code ON prescription_diseases (drug_code);

-- ---------- 2. 事实表常用分组列 ----------
CREATE INDEX idx_diag1      ON prescription_diseases (m_diagnostic1);
CREATE INDEX idx_section    ON prescription_diseases (m_section);
CREATE INDEX idx_hospid     ON prescription_diseases (hosp_id);

-- ---------- 3. 维表关联键 ----------
CREATE INDEX idx_sec_section2   ON t_view_section (section2);
CREATE INDEX idx_dis_type13     ON t_view_disease (disease_type13);
CREATE INDEX idx_hosp_hospid    ON t_view_hosp (hosp_id);
CREATE INDEX idx_areas_hospid   ON t_view_areas (hosp_id);
CREATE INDEX idx_drug_drug      ON t_view_drug (drug);

-- ---------- 4. 校验 ----------
SELECT COUNT(*) AS drug_code_rows FROM prescription_diseases WHERE drug_code IS NOT NULL;
SHOW INDEX FROM prescription_diseases;
